#!/usr/bin/env python3
"""
Step 4: 5-step ZI ID assignment pipeline.

Reads intermediate/current_issues.json and intermediate/prior_zi_assignments.json
Outputs intermediate/zi_assignments.json
"""

import json
from pathlib import Path


def jaccard_similarity(str1, str2):
    """Calculate Jaccard similarity between two strings based on token overlap."""
    tokens1 = set(str1.split())
    tokens2 = set(str2.split())

    if not tokens1 or not tokens2:
        return 0.0

    intersection = len(tokens1 & tokens2)
    union = len(tokens1 | tokens2)

    return intersection / union if union > 0 else 0.0


def step_1_exact_match(current_issues, prior_zis):
    """Step 4.1: Exact match - preserve prior ZIs."""
    assignments = []
    unassigned = []

    print("\n=== Step 4.1: Exact Match ===")

    for ticket_id, ticket_info in current_issues.items():
        for issue in ticket_info['issues']:
            matched = False

            # Search for exact match (same ticket_id AND normalized_title)
            for zi_id, zi_info in prior_zis.items():
                if (zi_info['ticket_id'] == ticket_id and
                    zi_info['normalized_title'] == issue['normalized_title']):

                    # Exact match found
                    assignments.append({
                        'zi': zi_id,
                        'ticket_id': ticket_id,
                        'title': issue['title'],
                        'normalized_title': issue['normalized_title'],
                        'product': ticket_info['product'],
                        'area': issue['area'],
                        'duplicate_of': None,
                        'assignment_type': 'exact_match'
                    })

                    # Mark ZI as referenced
                    zi_info['referenced'] = True
                    matched = True
                    break

            if not matched:
                unassigned.append({
                    'ticket_id': ticket_id,
                    'issue': issue,
                    'product': ticket_info['product']
                })

    print(f"  Exact matches: {len(assignments)}")
    print(f"  Unassigned: {len(unassigned)}")

    return assignments, unassigned


def step_2_fuzzy_duplicate(unassigned, prior_zis, next_zi):
    """Step 4.2: First-pass fuzzy match - duplicate detection within same ticket."""
    assignments = []
    remaining_unassigned = []

    print("\n=== Step 4.2: Fuzzy Duplicate Detection ===")

    threshold = 0.4

    for item in unassigned:
        ticket_id = item['ticket_id']
        issue = item['issue']
        matched = False

        # Search prior_zis on SAME ticket with different title
        for zi_id, zi_info in prior_zis.items():
            if zi_info['ticket_id'] != ticket_id:
                continue

            if zi_info['normalized_title'] == issue['normalized_title']:
                continue  # Skip exact matches (already handled)

            # Calculate Jaccard similarity
            similarity = jaccard_similarity(
                zi_info['normalized_title'],
                issue['normalized_title']
            )

            if similarity >= threshold:
                # Fuzzy match found - this is likely a duplicate
                new_zi = f"ZI-{next_zi}"
                next_zi += 1

                assignments.append({
                    'zi': new_zi,
                    'ticket_id': ticket_id,
                    'title': issue['title'],
                    'normalized_title': issue['normalized_title'],
                    'product': item['product'],
                    'area': issue['area'],
                    'duplicate_of': zi_id,
                    'assignment_type': 'fuzzy_duplicate',
                    'similarity': similarity
                })

                # DO NOT mark prior ZI as referenced - let it be carried forward
                # The new ZI will reference it as a duplicate
                matched = True
                break

        if not matched:
            remaining_unassigned.append(item)

    print(f"  Fuzzy duplicates: {len(assignments)}")
    print(f"  Still unassigned: {len(remaining_unassigned)}")

    return assignments, remaining_unassigned, next_zi


def step_3_fresh_assignment(unassigned, next_zi):
    """Step 4.3: Fresh assignment for genuinely new issues."""
    assignments = []

    print("\n=== Step 4.3: Fresh Assignment ===")

    for item in unassigned:
        new_zi = f"ZI-{next_zi}"
        next_zi += 1

        assignments.append({
            'zi': new_zi,
            'ticket_id': item['ticket_id'],
            'title': item['issue']['title'],
            'normalized_title': item['issue']['normalized_title'],
            'product': item['product'],
            'area': item['issue']['area'],
            'duplicate_of': None,
            'assignment_type': 'fresh'
        })

    print(f"  Fresh assignments: {len(assignments)}")

    return assignments, next_zi


def step_4_cross_reference(new_assignments):
    """Step 4.4: Second-pass cross-reference - find duplicates among new ZIs."""
    print("\n=== Step 4.4: Cross-Reference (within new ZIs) ===")

    threshold = 0.4
    duplicates_found = 0

    # Group new ZIs by ticket
    by_ticket = {}
    for assignment in new_assignments:
        ticket_id = assignment['ticket_id']
        if ticket_id not in by_ticket:
            by_ticket[ticket_id] = []
        by_ticket[ticket_id].append(assignment)

    # For each ticket with multiple new ZIs, check for duplicates
    for ticket_id, issues in by_ticket.items():
        if len(issues) <= 1:
            continue

        # Compare each pair
        for i, issue1 in enumerate(issues):
            if issue1['duplicate_of']:  # Already marked as duplicate
                continue

            for issue2 in issues[i + 1:]:
                if issue2['duplicate_of']:  # Already marked as duplicate
                    continue

                similarity = jaccard_similarity(
                    issue1['normalized_title'],
                    issue2['normalized_title']
                )

                if similarity >= threshold:
                    # Get ZI numbers
                    zi1_num = int(issue1['zi'].split('-')[1])
                    zi2_num = int(issue2['zi'].split('-')[1])

                    # Mark the higher-numbered ZI as duplicate of lower
                    if zi1_num < zi2_num:
                        issue2['duplicate_of'] = issue1['zi']
                        duplicates_found += 1
                    else:
                        issue1['duplicate_of'] = issue2['zi']
                        duplicates_found += 1

    print(f"  Cross-reference duplicates: {duplicates_found}")

    return new_assignments


def step_5_carry_forward(prior_zis):
    """Step 4.5: Carry forward unreferenced prior ZIs."""
    assignments = []

    print("\n=== Step 4.5: Carry Forward ===")

    for zi_id, zi_info in prior_zis.items():
        if not zi_info['referenced']:
            assignments.append({
                'zi': zi_id,
                'ticket_id': zi_info['ticket_id'],
                'title': zi_info['title'],
                'normalized_title': zi_info['normalized_title'],
                'product': zi_info['product'],
                'area': zi_info['area'],
                'duplicate_of': None,
                'assignment_type': 'carry_forward'
            })

    print(f"  Carried forward: {len(assignments)}")

    return assignments


def main():
    # Load inputs
    intermediate_dir = Path(__file__).parent.parent / 'intermediate'

    current_issues_path = intermediate_dir / 'current_issues.json'
    prior_zis_path = intermediate_dir / 'prior_zi_assignments.json'

    if not current_issues_path.exists():
        print(f"Error: {current_issues_path} not found. Run load_summaries.py first.")
        return

    if not prior_zis_path.exists():
        print(f"Error: {prior_zis_path} not found. Run load_prior_index.py first.")
        return

    with open(current_issues_path, 'r') as f:
        current_issues = json.load(f)

    with open(prior_zis_path, 'r') as f:
        prior_zis = json.load(f)

    # Find next ZI number
    max_prior_zi = max(int(zi.split('-')[1]) for zi in prior_zis.keys())
    next_zi = max_prior_zi + 1

    print(f"Starting ZI assignment pipeline")
    print(f"Current issues: {sum(len(t['issues']) for t in current_issues.values())} issues across {len(current_issues)} tickets")
    print(f"Prior ZIs: {len(prior_zis)} (ZI-136 to ZI-{max_prior_zi})")
    print(f"Next ZI: ZI-{next_zi}")

    # Run 5-step pipeline
    all_assignments = []

    # Step 1: Exact match
    exact_matches, unassigned = step_1_exact_match(current_issues, prior_zis)
    all_assignments.extend(exact_matches)

    # Step 2: Fuzzy duplicate detection
    fuzzy_duplicates, unassigned, next_zi = step_2_fuzzy_duplicate(unassigned, prior_zis, next_zi)

    # Step 3: Fresh assignment
    fresh_assignments, next_zi = step_3_fresh_assignment(unassigned, next_zi)

    # Step 4: Cross-reference among new ZIs
    new_assignments = fuzzy_duplicates + fresh_assignments
    new_assignments = step_4_cross_reference(new_assignments)
    all_assignments.extend(new_assignments)

    # Step 5: Carry forward unreferenced prior ZIs
    carried_forward = step_5_carry_forward(prior_zis)
    all_assignments.extend(carried_forward)

    # Sort by ZI number
    all_assignments.sort(key=lambda x: int(x['zi'].split('-')[1]))

    # Write output
    output_path = intermediate_dir / 'zi_assignments.json'

    with open(output_path, 'w') as f:
        json.dump(all_assignments, f, indent=2)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total ZI assignments: {len(all_assignments)}")
    print(f"  Exact matches: {len(exact_matches)}")
    print(f"  Fuzzy duplicates: {len(fuzzy_duplicates)}")
    print(f"  Fresh assignments: {len(fresh_assignments)}")
    print(f"  Carried forward: {len(carried_forward)}")
    print(f"Highest ZI: ZI-{next_zi - 1}")
    print(f"✓ Wrote: {output_path}")

    # Validate all prior ZIs are present
    assigned_zis = set(a['zi'] for a in all_assignments)
    prior_zi_ids = set(prior_zis.keys())
    missing = prior_zi_ids - assigned_zis

    if missing:
        print(f"\n⚠️  WARNING: {len(missing)} prior ZIs not in output: {sorted(missing)[:10]}")
    else:
        print(f"\n✓ All {len(prior_zis)} prior ZI IDs preserved")


if __name__ == '__main__':
    main()
