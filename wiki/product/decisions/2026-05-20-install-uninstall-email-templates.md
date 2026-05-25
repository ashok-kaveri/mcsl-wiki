---
title: "Install/uninstall emails: direct send from MCSL; NO Zendesk tickets"
category: product-decision
status: accepted
date: 2026-05-20
git_reference: current
---

# Install/uninstall emails: direct send from MCSL; NO Zendesk tickets

## Context

Today every install / uninstall hits `routes/storepepConnector.js:514` (install) and `:584` (uninstall) and calls `createTicket(constants.INSTALLATION, ...)` / `createTicket(constants.UNINSTALLATION, ...)`. That helper POSTs to the Zendesk Tickets API at `shared/adminNotification/zendeskHelper.js:87`. Two problems:

1. **Noise**: a ticket is created in Zendesk for every install/uninstall event whether the merchant ever wanted help or not. Support cannot prioritise real customer queries against this background — surfaced on #387845 and #390467.
2. **Self-sent welcome email**: the ticket's `requester` is set to the merchant's own email (`shared/adminNotification/zendeskTemplates.js:1-7`). Zendesk's outbound trigger uses the requester identity, so the welcome email appears to come FROM the merchant TO the merchant. Lands in spam.

This decision resolves both.

## Decision

**1. Stop creating Zendesk tickets from MCSL on install/uninstall.**

The `createTicket(INSTALLATION, ...)` call at `routes/storepepConnector.js:514` and the `createTicket(UNINSTALLATION, ...)` call at `:584` are removed. The MCSL→Zendesk POST for these two lifecycle events is gone. `createZendeskTicket()` itself remains in `zendeskHelper.js` because other ticket types (`SIGNUP`, `SUBSCRIPTION_ABOUT_TO_EXPIRE`, `PAYMENT_ERROR`) still use it; only the `INSTALLATION` and `UNINSTALLATION` cases are removed.

**2. Send the install/uninstall email directly from MCSL.**

MCSL calls a new direct mailer helper (`shared/storepepMailer/storepepMails.js → sendInstallationEmail` / `sendUninstallationEmail`) using the existing `sendMail` primitive. The email envelope is:

- **From**: `PluginHive Onboarding <onboarding@pluginhive.com>` (or per-app variant — see templates below). Configurable; not a hard-coded individual name.
- **Reply-To**: `support@pluginhive.com`
- **To**: `${userFromDb.email}`
- **Subject + HTML body**: per-app, per-event (install vs uninstall) — drafts below

**3. Zendesk tickets are created ONLY when the merchant replies.**

A merchant reply to the welcome email lands at `support@pluginhive.com`, which is wired into Zendesk's inbound-email channel. Zendesk creates a fresh ticket on inbound — exactly the "tickets are for real conversations" pattern, and the only legitimate way for an install/uninstall to spawn a Zendesk ticket.

**4. Replacement ops signal for install visibility.**

CSM teams currently use "ticket per install" as their install-tracking signal. After this decision lands, the signal moves to either (a) a Slack notification on the existing `AppInstalled` / `AppUnInstalled` analytics event in `shared/events/index.js:26-49`, or (b) a CSM dashboard view fed by the same analytics pipeline. **Install visibility cannot be lost** — the replacement signal must be live before the Zendesk-ticket removal ships.

## Alternatives considered

- **Just change the `requester` block** (the original ZI-530 reassessment) — would fix the self-sent email shape but does nothing about the noise problem (still creates a ticket per install). Rejected.
- **Keep Zendesk tickets, suppress outbound auto-reply email** — half-measure; still creates Zendesk noise. Rejected.
- **Move to a marketing-automation tool (HubSpot, Customer.io)** — broader scope, longer lead time; not in this release window. Park for later.

## Signals

- Zendesk: [#387845](../../zendesk/summaries/387845.md) (smartbot-hobot / José — the case where Mirdas flagged the self-sent welcome email)
- Zendesk: [#390467](../../zendesk/summaries/390467.md) (end-customer complaint landing at PluginHive — same SMTP-related root cause, different angle)
- Product owner direction: 2026-05-20 (verbal): "we do not want these installation/uninstallation emails to be created as Zendesk tickets… create tickets only when the customer replies"

## Consequences

**Positive**:
- Zendesk ticket volume drops by one ticket per install + one per uninstall × all PluginHive Shopify apps. Support team's "real customer queries" signal gets noticeably cleaner.
- Welcome email goes from "self-sent shape, spam folder" to "from a recognisable PluginHive identity, reply-routes back to support" — better deliverability + a real conversation channel when needed.

**Negative / things to manage**:
- **CSM loses install/uninstall visibility from Zendesk views**. The replacement Slack/dashboard signal MUST be live before this ships, otherwise install tracking disappears.
- **Zendesk views/macros/automations that filter on `tags: wss_installation` or sibling app tags will stop firing**. Audit + update them with the Zendesk admin before deploy.
- **SPF/DKIM/DMARC alignment** on `onboarding@pluginhive.com` (and per-app variants if used) is critical — the whole point of the change is deliverability.

## Related

- Card: ZI-530 — [trello.com/c/m9W9Cblq](https://trello.com/c/m9W9Cblq)
- Companion card: ZI-552 ([trello.com/c/1tE8cry4](https://trello.com/c/1tE8cry4)) — separate decision to suppress merchant-recipient tracking-notification emails when merchant SMTP isn't configured (different flow, different fix, complementary direction)
- Backlog: [Active backlog](../backlog.md)
- Module reference: `routes/storepepConnector.js`, `shared/storepepMailer/storepepMails.js`, `shared/adminNotification/zendeskTemplates.js`, `shared/adminNotification/zendeskHelper.js`

---

# Code changes summary (engineering reference)

**Mandatory removals:**

1. `routes/storepepConnector.js:514` — DELETE `await createTicket(constants.INSTALLATION, storeFromDb, userFromDb, updatedUserAccount || userAccountFromDb);` (and its `if (!isZendeskTicketAndEmailAlertDisabled)` wrapper if no longer needed). After this line, `EventPublisher.emit(new AppInstalled(...))` still fires — the analytics event is preserved.
2. `routes/storepepConnector.js:584` — DELETE `await createTicket(constants.UNINSTALLATION, data, userFromDb, userAccount);` (analogous).
3. `routes/storepepConnector.js:60-72` — DELETE the `ticketBodyMapper` object and the `createTicket` helper function. They have no other callers after the install/uninstall paths stop using them.
4. `shared/adminNotification/zendeskTemplates.js` — DELETE the `getZendeskInstallationTemplate` and `getZendeskUninstallationTemplate` exports (or leave deprecated stubs for transition). REPLACE with body-only helpers `getInstallationEmailHtml(...)` / `getUninstallationEmailHtml(...)` returning just the HTML body, no Zendesk ticket payload wrapper.

**Mandatory additions:**

1. `shared/storepepMailer/storepepMails.js` — ADD `sendInstallationEmail(store, user, account, app)` and `sendUninstallationEmail(store, user, account, app)` helpers. Use existing `sendMail(mailContent, mailSettings)` primitive. Build the mail envelope per the templates below. The `app` parameter selects the per-app variant ("mcsl" | "wss" | "fedex" | "auspost" | "shipment-tracking").
2. `routes/storepepConnector.js:514, 584` — call the new helpers in place of the removed `createTicket` calls.
3. New analytics signal: either Slack notification or dashboard event on the existing `AppInstalled` / `AppUnInstalled` events (no schema change; the events already carry merchant identity + store URL).

**Mandatory non-code:**

- Zendesk admin: confirm `support@pluginhive.com` inbound channel routes to the right queue.
- Zendesk admin: audit views/macros/automations filtered on `tags: wss_installation` / `wss_uninstallation` / app equivalents — they will stop firing.
- DNS / mail-sender: verify SPF / DKIM / DMARC alignment for `onboarding@pluginhive.com` (or per-app variants).

---

# Email templates

All templates use `${user.firstName}` and `${store.url}` as the only required substitutions. Avoid hard-coding individual names in the rendered output — sign as "Customer Success Manager / Team PluginHive" generically, or pass the assigned CSM name as a parameter resolved from the carrier-success rotation (TBD; the dev team's choice).

For each app, two templates: **install** (welcome) and **uninstall** (win-back).

---

## 1. Shopify FedEx Shipping app (`shopify_fedex_app`)

### Install

```
Subject: Start Printing FedEx Labels & Show Rates on ${store.url} Today

Hello ${user.firstName},

Greetings from PluginHive!

Thank you for installing the Shopify FedEx Shipping app on ${store.url}.

Connect your FedEx account to start printing FedEx labels and showing live
FedEx rates at checkout today.

We also offer a free 30-minute onboarding Zoom call to help you complete
the setup quickly.

Please let us know your availability, or schedule a call here: <CALENDLY_LINK>

You can also refer to our setup documentation here: <DOCS_LINK>

Thanks and Regards,
Customer Success Manager
Team PluginHive
```

### Uninstall

```
Subject: Sorry to see you go from ${store.url}

Hello ${user.firstName},

We noticed you uninstalled the Shopify FedEx Shipping app from ${store.url}.

If there's anything we could have done better, we'd love to hear it — reply
to this email and a real person will read every word.

If you uninstalled because the setup felt hard, we'd be happy to walk you
through it on a 30-minute Zoom call at no cost. Schedule here: <CALENDLY_LINK>

Either way — thanks for trying us.

Customer Success Manager
Team PluginHive
```

---

## 2. Shopify Multi Carrier Shipping Label App (MCSL)

### Install

```
Subject: Start Generating Multi-Carrier Labels on ${store.url} Today

Hello ${user.firstName},

Greetings from PluginHive!

Thank you for installing the Multi Carrier Shipping Label app on ${store.url}.

MCSL supports 30+ carriers including FedEx, UPS, USPS, DHL, Australia Post,
Canada Post, PostNord, Amazon Shipping India, Delhivery and more — connect
your carrier accounts to start printing labels and showing live rates today.

We offer a free 30-minute onboarding Zoom call to help you connect your
first carrier and configure automation rules. Please let us know your
availability, or schedule a call here: <CALENDLY_LINK>

You can also refer to our setup documentation here: <DOCS_LINK>

Thanks and Regards,
Customer Success Manager
Team PluginHive
```

### Uninstall

```
Subject: Sorry to see you go from ${store.url}

Hello ${user.firstName},

We noticed you uninstalled MCSL from ${store.url}.

If there's anything we could have done better — a missing carrier, a confusing
setting, a billing surprise — we'd love to hear it. Reply to this email and
a real person will read every word.

If you uninstalled because the setup or a specific carrier felt hard, we'd
be happy to walk you through it on a 30-minute Zoom call at no cost. Schedule
here: <CALENDLY_LINK>

Either way — thanks for trying us.

Customer Success Manager
Team PluginHive
```

---

## 3. WooCommerce Shipping Services Plugin (WSS)

### Install

```
Subject: Start Showing Live Shipping Rates on ${store.url} Today

Hello ${user.firstName},

Greetings from PluginHive!

Thank you for installing the WooCommerce Shipping Services plugin on ${store.url}.

Connect your shipping carriers to show live rates at checkout and start
printing labels today. We support FedEx, UPS, USPS, DHL, Australia Post,
Canada Post, PostNord, and many more.

We offer a free 30-minute onboarding Zoom call to help you connect your
first carrier and configure rates. Please let us know your availability,
or schedule a call here: <CALENDLY_LINK>

You can also refer to our setup documentation here: <DOCS_LINK>

Thanks and Regards,
Customer Success Manager
Team PluginHive
```

### Uninstall

```
Subject: Sorry to see you go from ${store.url}

Hello ${user.firstName},

We noticed you uninstalled the WooCommerce Shipping Services plugin from
${store.url}.

If there's anything we could have done better — a missing carrier, a confusing
setting, an integration glitch — we'd love to hear it. Reply to this email
and a real person will read every word.

If you uninstalled because the setup felt hard, we'd be happy to walk you
through it on a 30-minute Zoom call at no cost. Schedule here: <CALENDLY_LINK>

Either way — thanks for trying us.

Customer Success Manager
Team PluginHive
```

---

## 4. Shopify Australia Post app

### Install

```
Subject: Start Printing Australia Post Labels on ${store.url} Today

Hello ${user.firstName},

Greetings from PluginHive!

Thank you for installing the Shopify Australia Post app on ${store.url}.

Connect your Australia Post eParcel or MyPost Business account to start
printing eParcel labels and showing live rates at checkout today.

A heads-up: from 4 August 2026, Australia Post requires every shipment to
carry a recipient phone number or email. Our app will help you flag any
orders missing this detail before the deadline.

We offer a free 30-minute onboarding Zoom call to help you complete the
setup. Please let us know your availability, or schedule a call here:
<CALENDLY_LINK>

You can also refer to our setup documentation here: <DOCS_LINK>

Thanks and Regards,
Customer Success Manager
Team PluginHive
```

### Uninstall

```
Subject: Sorry to see you go from ${store.url}

Hello ${user.firstName},

We noticed you uninstalled the Shopify Australia Post app from ${store.url}.

If there's anything we could have done better — eParcel setup, MPB
authentication, a confusing service code — we'd love to hear it. Reply to
this email and a real person will read every word.

If you uninstalled because the setup felt hard, we'd be happy to walk you
through it on a 30-minute Zoom call at no cost. Schedule here: <CALENDLY_LINK>

Either way — thanks for trying us.

Customer Success Manager
Team PluginHive
```

---

## 5. Shopify Shipment Tracking app

### Install

```
Subject: Start Sending Tracking Updates from ${store.url} Today

Hello ${user.firstName},

Greetings from PluginHive!

Thank you for installing the Shipment Tracking app on ${store.url}.

Our app automatically pulls tracking events from your carriers and sends
branded tracking notifications to your customers — without sharing your
data with anyone else.

A note on email sending: by default, our app only sends tracking notifications
when you've configured your own SMTP. This keeps your customer
communications under your domain — better deliverability, and your customers
reply to YOU, not to us.

We offer a free 30-minute onboarding Zoom call to help you connect your
carriers and configure SMTP. Please let us know your availability, or
schedule a call here: <CALENDLY_LINK>

You can also refer to our setup documentation here: <DOCS_LINK>

Thanks and Regards,
Customer Success Manager
Team PluginHive
```

### Uninstall

```
Subject: Sorry to see you go from ${store.url}

Hello ${user.firstName},

We noticed you uninstalled the Shipment Tracking app from ${store.url}.

If there's anything we could have done better — a missing carrier, an SMTP
gotcha, a tracking email template that didn't fit your brand — we'd love
to hear it. Reply to this email and a real person will read every word.

If you uninstalled because the setup felt hard, we'd be happy to walk you
through it on a 30-minute Zoom call at no cost. Schedule here: <CALENDLY_LINK>

Either way — thanks for trying us.

Customer Success Manager
Team PluginHive
```

---

# Open questions for the team

- **CSM identity** — generic alias (`onboarding@pluginhive.com` + "Customer Success Manager" signature) vs per-merchant assignment (named CSM rotated per region/volume)? My recommendation: generic alias initially; layer in per-merchant assignment once the rotation rule is defined.
- **`<CALENDLY_LINK>` / `<DOCS_LINK>` source** — config in `storepepConfig.js` per app, or hard-coded constants per template helper? Recommendation: config per app, so each app's CSM team can own their own link.
- **Uninstall email send delay** — send immediately on uninstall, or delay 24-48h to filter out accidental uninstalls + reinstalls? Recommendation: 24h delay with a `cancelled-on-reinstall` debounce hook on the `AppInstalled` event.
- **Email open / click tracking** — track engagement on these direct sends (for CSM follow-up)? Recommendation: yes, via Mailgun / SendGrid open tracking — but separately decided since it requires a privacy disclosure.
