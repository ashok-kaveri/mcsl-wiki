---
date: 2026-04-15
channel: "#engineering"
participants: [Mohammed Muzammil Anwar, Mirdas, Keerthi, Abhilash S]
related:
  zendesk: 379963
  zi: ZI-057
  trello: "https://trello.com/c/DxVXh1CF/4129"
topic: Royal Mail carrier integration via EasyPost — test credentials and 3PI requirements
---

# Royal Mail EasyPost Integration Discussion

Mohammed Muzammil Anwar  [2:01 PM]
@here we will need to add royal mail as a carrier from the easypost dashboard!? for us and the qa team to test this card!?
https://trello.com/c/DxVXh1CF/4129-from-sl-zi-057-royalmail48parceldailyrateservice-missing-from-app-379963

Mohammed Muzammil Anwar  [3:59 PM]
@Mirdas sir, this might be something we need partnerships to look into?!

Mirdas  [5:10 PM]
@Mohammed Muzammil Anwar I guess we already have customers using easy post via Royal mail .. Not sure whether I understood the question  @Keerthi please confirm ..

[5:11 PM]
In general, we should be able to add all carriers via Easy post .

[5:12 PM]
(All carriers supported by EasyPost)

Mohammed Muzammil Anwar  [5:12 PM]
well for our credentials, we need to login to easypost dashboard and then add a carrier... right now in QA we do not have royal mail configured via easypost

Mirdas  [5:13 PM]
Ok got it

[5:13 PM]
@Abhilash S @Keerthi can you help here :point_up:

Keerthi  [5:16 PM]
@Mirdas RoyalMail cannot be integrated directly.
Merchants need an OBA account, posting location ID and also share their OBA account rates card to EasyPost team. EasyPost team will then contact RoyalMail and get approval and upload that Rates card to merchant's RoyalMail account connected via EasyPost.

Mirdas  [5:33 PM]
Yeah , I remember, can we arrange a test account for Dev and QA?

[5:35 PM]
From easy post to test royal mail

Keerthi  [5:36 PM]
I recall we contacted EasyPost team in the past and requested them to share test credentials with us, but they were unable to help at that time. We can reach out again and check.
@Abhilash S, would you be able to initiate the conversation from your end and also cc me?

Abhilash S  [6:02 PM]
@Mirdas We cannot reliably support Royal Mail integration without becoming an approved 3PI. For software providers, Direct API access is not freely available, Integration typically requires going through Intersoft or similar approved partner infrastructure.

(There is no free production-ready API available for PluginHive or any multi-carrier / SaaS platforms)

Applies to both:

BYOA (Bring Your Own Account)
Reseller models

@Vimal @Keerthi FYI

[6:03 PM]
@Mirdas @Keerthi I will explore Easypost route to access Royal Mail. Let me get in touch with them to get a test account so we can test royal mail.
