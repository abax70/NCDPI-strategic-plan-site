"""Apply sniff-test review and coverage analysis to produce reviewed matches CSV."""
import csv
from collections import Counter

# Blog metadata
blogs = {}
with open('data/blog_posts.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader, 1):
        blogs[i] = row

pillar_names = {
    'P1': 'Prepare Each Student for Their Next Phase in Life',
    'P2': 'Invest in Educators',
    'P3': 'Engage and Empower Families and Communities',
    'P4': 'Support Student Health and Well-Being',
    'P5': 'Strengthen NCDPI Leadership and Support Services',
    'P6': 'Foster Innovation and Continuous Improvement',
    'P7': 'Advance Public Education Communications',
    'P8': 'Build Community Advocacy'
}

fa_names = {
    'P1.F1': 'Ignite early learning',
    'P1.F2': 'Elevate teaching and learning',
    'P1.F3': 'Promote excellence for all',
    'P1.F4': 'Reimagine the student experience',
    'P1.F5': 'Launch life-ready graduates',
    'P2.F1': 'Improve educator recruitment and retention',
    'P2.F2': 'Expand career pathways for education professionals',
    'P2.F3': 'Increase educator compensation',
    'P2.F4': 'Elevate and restore pride in the education profession',
    'P3.F1': 'Engage and empower families',
    'P3.F2': 'Strengthen community partnerships',
    'P4.F1': 'Ensure safe school environments',
    'P4.F2': 'Improve student and staff health and well-being',
    'P5.F1': "Improve NCDPI's services to stakeholders",
    'P5.F2': 'Improve collaboration and communication across NCDPI offices',
    'P5.F3': 'Modernize NCDPI and PSU operations',
    'P6.F1': 'Transform schools through research and development',
    'P6.F2': 'Connect NC public schools through education networks',
    'P6.F3': 'Promote integrated support systems for schools and districts',
    'P6.F4': 'Explore accountability and funding reform',
    'P7.F1': 'Develop comprehensive public education messaging',
    'P7.F2': 'Engage partners on education',
    'P7.F3': 'Share public education messaging and stories',
    'P8.F1': 'Build community voices',
    'P8.F2': 'Promote engagement initiatives',
    'P8.F3': 'Move champions to action'
}

# ======================================================================
# ORIGINAL 82 matches (from Phase 2)
# ======================================================================
original_matches = [
    (1, 'P1.F3', 'Blog discusses CTE and rigorous pathways as part of strategic plan goals'),
    (1, 'P1.F4', 'Career/college readiness is a central theme, aligning with career development plans'),
    (1, 'P2.F3', 'Educator compensation explicitly named as a strategic plan theme'),
    (2, 'P1.F3', 'Dual language immersion and Global Ready District are rigorous academic pathways'),
    (2, 'P1.F5', 'Workforce readiness and global leadership are durable skills for postsecondary success'),
    (2, 'P1.F2', 'K-12 dual language immersion is a systematic instructional framework'),
    (3, 'P2.F4', 'Teacher of the Year recognition is a named action under P2.F4'),
    (3, 'P1.F4', 'AVID program and Kenan Fellows career exploration support career development'),
    (3, 'P3.F2', 'Grow Local and Kenan Fellows are community partnerships supporting schools'),
    (4, 'P6.F1', 'ORPP identifying and evaluating effective practices mirrors P6.F1 actions'),
    (4, 'P4.F2', 'Chronic absenteeism discussed as a research focus, a named P4.F2 action'),
    (4, 'P5.F3', 'Data framework and analytics align with NCDPI data/analytics modernization'),
    (5, 'P4.F2', 'Chronic absenteeism reduction is a named action under P4.F2'),
    (6, 'P4.F2', 'Staff wellness and mental health support align with staff health/well-being'),
    (6, 'P3.F2', 'Schools as community support systems during disaster recovery'),
    (7, 'P3.F2', 'Schools as lifelines for community healing exemplifies PSU-community bridge'),
    (7, 'P4.F2', 'Community healing aligns with whole school/community well-being model'),
    (8, 'P2.F4', 'Principal of the Year recognition is a named action under P2.F4'),
    (8, 'P2.F3', 'Blog explicitly discusses advocacy for educator compensation'),
    (8, 'P1.F3', 'Equitable access and 100% growth aligns with excellence for all'),  # WEAK -> CUT
    (9, 'P1.F3', 'CTE at 36% participation is a rigorous career pathway'),
    (9, 'P1.F4', 'Early college, Farm to School, and workforce development reimagine student experience'),
    (9, 'P1.F5', 'Workforce development and career readiness support life-ready graduates'),
    (9, 'P3.F2', 'Farm to School is a community/business partnership supporting schools'),
    (10, 'P1.F4', 'NC College Connect and direct admission are named actions under P1.F4'),
    (10, 'P1.F5', 'College spots for 70,000 seniors is a direct postsecondary launch mechanism'),
    (11, 'P4.F2', 'School nutrition directly aligns with student health actions under P4.F2'),
    (11, 'P3.F2', 'Farm-to-School partnerships are community/business partnerships'),
    (12, 'P1.F3', 'Advanced manufacturing, healthcare CTE are rigorous career/academic pathways'),
    (12, 'P1.F4', 'Zoo School experiential learning reimagines the student experience'),
    (12, 'P6.F1', 'Global Innovation Center and Zoo School are innovative school practices'),
    (13, 'P1.F4', 'Student advisor shaping State Board policy reimagines student voice'),
    (13, 'P1.F3', 'Transcript and class weighting relates to equitable access to rigorous pathways'),  # WEAK -> CUT
    (14, 'P3.F1', 'Parent University is a direct family engagement initiative'),
    (14, 'P1.F3', 'Content covers CTE and dual language pathway options'),  # WEAK -> CUT
    (15, 'P1.F3', 'STEM, robotics, CTE, and AVID are rigorous academic and career pathways'),
    (15, 'P1.F2', 'STEM and digital learning tools align with elevating teaching'),
    (15, 'P2.F2', 'Teacher Advisory Councils represent teacher leadership pathways'),
    (16, 'P1.F3', '550,000+ CTE participants with 98% graduation rate'),
    (16, 'P1.F4', 'Career development coordinators are a named P1.F4 action'),
    (16, 'P1.F5', 'Work-based learning directly launches life-ready graduates'),
    (17, 'P1.F3', 'Early college with diploma + associate degree is a rigorous pathway'),
    (17, 'P1.F4', 'Legal internship and Teen Court are career development experiences'),
    (17, 'P1.F5', 'Diploma + associate degree + internship = life-ready graduate'),
    (18, 'P1.F4', 'Student advisory council giving students policy voice reimagines student experience'),
    (18, 'P2.F3', 'Teacher compensation named as a student priority'),  # WEAK -> CUT
    (18, 'P4.F2', 'Mental health named as a student advisory council priority'),
    (19, 'P1.F4', 'Student newspaper is an arts/leadership extracurricular under P1.F4'),
    (19, 'P1.F5', 'Student journalism and UNC pipeline represent durable skills'),
    (20, 'P1.F4', 'College-going culture and experiential learning reimagine student experience'),
    (20, 'P1.F3', 'Career/college prep pathways are rigorous academic pathways'),
    (20, 'P1.F5', 'College-going culture launches life-ready graduates'),
    (21, 'P1.F3', 'CTE and dual enrollment are rigorous career/academic pathways'),
    (21, 'P2.F1', 'UNC Pembroke teacher prep is a direct educator recruitment pipeline'),
    (21, 'P1.F5', 'Workforce development with AWS supports life-ready graduates'),
    (21, 'P3.F2', 'AWS and UNC Pembroke are business/higher-ed community partnerships'),
    (22, 'P1.F3', 'Jr. Chef Competition is CTE culinary arts'),
    (22, 'P4.F2', 'Nutritious school lunches support student health'),
    (23, 'P1.F5', 'Portrait of a Graduate skills are durable skills for life readiness'),
    (23, 'P4.F2', 'Bike safety unit aligns with physical activity promotion under P4.F2'),
    (23, 'P1.F1', 'Cross-grade peer mentorship in elementary school'),  # WEAK -> CUT
    (24, 'P1.F3', 'CTE and dual language immersion are rigorous pathways'),
    (24, 'P2.F1', 'Appalachian State teacher prep is a direct pipeline initiative'),
    (24, 'P3.F2', 'Teacher prep partnership and community rebuilding are partnerships'),
    (25, 'P2.F4', 'Teachers/Principals of the Year recognition actions under P2.F4'),
    (25, 'P1.F1', 'Early literacy explicitly mentioned as a point of pride'),
    (25, 'P1.F2', 'STEM and arts integration are elevated teaching approaches'),
    (25, 'P1.F4', 'Student belonging and arts integration represent reimagined experiences'),
    (26, 'P2.F4', 'Educators sharing resolutions elevates professional pride'),
    (26, 'P8.F1', 'Educators articulating advocacy resolutions builds community voices'),
    (27, 'P4.F2', 'School nutrition serving 850,000+ students supports student health'),
    (27, 'P3.F2', 'Boys & Girls Clubs, food banks, YMCAs are community partners'),
    (28, 'P1.F2', 'Place-based, inquiry-driven history instruction is elevated teaching'),
    (28, 'P1.F5', 'Civic engagement and service learning are named P1.F5 actions'),
    (28, 'P3.F2', 'Local civil rights stories are classroom-community partnership'),
    (28, 'P2.F4', 'National History Teacher recognition elevates the profession'),
    (29, 'P2.F1', 'Alternative pathways and grow-your-own are named teacher pipeline actions'),
    (29, 'P2.F2', 'Bus driver to EC teacher is a literal career pathway in education'),
    (29, 'P1.F3', 'EC education relates to equitable services for all'),  # WEAK -> CUT
    (30, 'P1.F3', 'Charter, early college, CTE with 160+ credentials are rigorous pathways'),
    (30, 'P1.F4', 'Helping families find the right school fit reimagines student experience'),
    (30, 'P3.F1', 'Campaign targets families to navigate educational options'),
]

# ======================================================================
# CUT LIST: matches flagged WEAK by reviewer and recommended for removal
# ======================================================================
cuts = {
    (8, 'P1.F3'),   # Principal profile is not about rigorous pathways
    (13, 'P1.F3'),  # Student advisory role is not about rigorous pathways
    (14, 'P1.F3'),  # Parent education about CTE != expanding CTE
    (18, 'P2.F3'),  # Students mentioning compensation != NCDPI advocating to legislature
    (23, 'P1.F1'),  # Bike safety at intermediate school != early learning (pre-K)
    (29, 'P1.F3'),  # Teacher recruitment story != expanding rigorous pathways
}

# Apply cuts
surviving = [(b, f, r) for b, f, r in original_matches if (b, f) not in cuts]
print(f'Original matches: {len(original_matches)}')
print(f'Cuts applied: {len(cuts)}')
print(f'Surviving: {len(surviving)}')

# ======================================================================
# NEW MATCHES from coverage analysis
# ======================================================================
new_matches = [
    # P7.F3: Share public education messaging and stories (success stories)
    (25, 'P7.F3', 'Points of Pride blog IS a success-stories narrative about NC public schools (P7.F3.A1)'),
    (30, 'P7.F3', 'Campaign highlighting diverse pathways IS sharing positive public education messaging (P7.F3.A2)'),
    (26, 'P7.F3', 'Educators sharing positive resolutions IS uplifting positive narratives about public education (P7.F3.A1)'),
    (3, 'P7.F3', 'Teacher of the Year profile IS a success story about a public school educator (P7.F3.A1)'),
    (8, 'P7.F3', 'Principal of the Year profile IS a success story about a public school leader (P7.F3.A1)'),
    (17, 'P7.F3', 'Student early college success story IS a positive narrative about NC public schools (P7.F3.A1)'),
    (29, 'P7.F3', 'Bus-driver-to-teacher story IS a positive narrative about the public education profession (P7.F3.A1)'),
    (28, 'P7.F3', 'National History Teacher of the Year IS a success story celebrating public education (P7.F3.A1)'),

    # P6.F2: Connect NC public schools through education networks (regional tours)
    (9, 'P6.F2', 'Southeast tour connects schools across regions, showcasing practices for cross-PSU learning (P6.F2.A1)'),
    (12, 'P6.F2', 'Piedmont Triad tour connects schools across districts, sharing innovations (P6.F2.A1)'),
    (15, 'P6.F2', 'Northeast tour connects rural schools, sharing STEM and CTE practices across counties (P6.F2.A1)'),
    (20, 'P6.F2', 'North Central tour connects schools, sharing college-going and experiential learning (P6.F2.A1)'),
    (21, 'P6.F2', 'Sandhills tour connects schools with partnerships like AWS and UNC Pembroke (P6.F2.A1)'),
    (24, 'P6.F2', 'Northwest tour connects schools, sharing CTE and dual language across counties (P6.F2.A1)'),

    # P8.F2: Promote engagement initiatives
    (14, 'P8.F2', 'Parent University is a district family engagement initiative matching P8.F2.A2 toolkits goal'),

    # P7.F1: Develop comprehensive public education messaging
    (1, 'P7.F1', 'Strategic plan unveiling IS comprehensive public education messaging developed through listening tour (P7.F1.A3)'),

    # P8.F3: Move champions to action
    (13, 'P8.F3', 'Student advisor to State Board is directly engaging policymakers on education (P8.F3.A1)'),
    (18, 'P8.F3', 'Student Advisory Council advises Superintendent on policy, a form of policymaker engagement (P8.F3.A1)'),
]

# Combine
all_matches = surviving + new_matches
print(f'New matches added: {len(new_matches)}')
print(f'Total final matches: {len(all_matches)}')

# Write reviewed CSV
with open('data/blog_focus_area_matches_reviewed.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['BlogNum', 'StoryTitle', 'StoryURL', 'StoryPublishDate', 'StoryCounty',
                     'FocusAreaID', 'FocusAreaName', 'PillarID', 'PillarName', 'MatchRationale'])
    for blog_num, fa_id, rationale in all_matches:
        b = blogs[blog_num]
        pid = fa_id.split('.')[0]
        writer.writerow([
            blog_num,
            b['StoryTitle'],
            b['StoryURL'],
            b['StoryPublishDate'],
            b['StoryCounty'],
            fa_id,
            fa_names.get(fa_id, ''),
            pid,
            pillar_names.get(pid, ''),
            rationale
        ])

print(f'\nWrote data/blog_focus_area_matches_reviewed.csv')

# Coverage stats
fa_counts = Counter(fa_id for _, fa_id, _ in all_matches)
blog_counts = Counter(bn for bn, _, _ in all_matches)
all_fas = set(fa_names.keys())
matched_fas = set(fa_counts.keys())
unmatched = all_fas - matched_fas

print(f'\n=== COVERAGE REPORT ===')
print(f'Focus areas with matches: {len(matched_fas)}/26')
print(f'Focus areas WITHOUT matches ({len(unmatched)}):')
for fa in sorted(unmatched):
    print(f'  {fa}: {fa_names[fa]}')

print(f'\nBlogs with matches: {len(blog_counts)}/30')
orphaned = set(range(1, 31)) - set(blog_counts.keys())
if orphaned:
    print(f'Orphaned blogs: {sorted(orphaned)}')
else:
    print('All 30 blogs have at least one match')

print('\nFocus area match distribution:')
for fa in sorted(fa_names.keys()):
    count = fa_counts.get(fa, 0)
    bar = '#' * count
    print(f'  {fa} ({fa_names[fa][:40]:40s}): {count:2d} {bar}')

print(f'\nMatches per blog:')
for bn in sorted(blog_counts.keys()):
    print(f'  Blog {bn:2d}: {blog_counts[bn]} matches')

# Pillar distribution
pillar_counts = Counter(fa_id.split('.')[0] for _, fa_id, _ in all_matches)
print(f'\nPillar distribution:')
for p in sorted(pillar_names.keys()):
    print(f'  {p}: {pillar_counts.get(p, 0)} matches')
