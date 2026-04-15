"""Build the draft matches CSV from matcher agent output."""
import csv
from collections import Counter

# Blog metadata from blog_posts.csv
blogs = {}
with open('data/blog_posts.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader, 1):
        blogs[i] = row

# Pillar names
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

# Focus area names
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

# All matches from the matcher agent
matches = [
    (1, 'P1.F3', 'Blog explicitly discusses CTE and rigorous pathways as part of strategic plan goals'),
    (1, 'P1.F4', 'Career/college readiness is a central theme, aligning with career development plans and postsecondary pathways'),
    (1, 'P2.F3', 'Educator compensation explicitly named as a strategic plan theme'),
    (2, 'P1.F3', 'Dual language immersion programs are rigorous academic pathways; Global Ready District is an advanced pathway'),
    (2, 'P1.F5', 'Workforce readiness and global leadership are durable skills for postsecondary success'),
    (2, 'P1.F2', 'K-12 dual language immersion is a systematic instructional framework across grade levels'),
    (3, 'P2.F4', 'Blog is about Teacher of the Year recognition, a named action under P2.F4'),
    (3, 'P1.F4', 'AVID program and Kenan Fellows career exploration directly support career development plans'),
    (3, 'P3.F2', 'Grow Local and Kenan Fellows are explicitly named community partnerships supporting schools'),
    (4, 'P6.F1', 'Blog is entirely about ORPP identifying and evaluating effective practices -- directly mirrors the focus area actions'),
    (4, 'P4.F2', 'Chronic absenteeism is explicitly discussed as a research focus, a named P4.F2 action'),
    (4, 'P5.F3', 'Data framework and analytics for decision-making align with NCDPI data/analytics modernization actions'),
    (5, 'P4.F2', 'Chronic absenteeism is a named action under P4.F2; blog is entirely about reducing absenteeism'),
    (6, 'P4.F2', 'Staff wellness programs directly align with student and staff health/well-being'),
    (6, 'P3.F2', 'Schools serving as community support systems during disaster recovery exemplifies PSU-community partnerships'),
    (7, 'P3.F2', 'Schools described as lifelines for community healing -- direct example of PSU-community bridge function'),
    (7, 'P4.F2', 'Community healing through schools aligns with the whole school/community well-being model'),
    (8, 'P2.F4', 'Principal of the Year recognition is a named action under P2.F4'),
    (8, 'P2.F3', 'Blog explicitly discusses advocacy for educator compensation'),
    (8, 'P1.F3', 'Equitable access and 100% growth across all schools aligns with excellence for all students'),
    (9, 'P1.F3', 'CTE at 36% participation is a rigorous career pathway; CTE is a named action area under P1.F3'),
    (9, 'P1.F4', 'Early college, Farm to School, and workforce development represent reimagined student experiences'),
    (9, 'P1.F5', 'Workforce development and career readiness directly support launching life-ready graduates'),
    (9, 'P3.F2', 'Farm to School is an explicit community/business partnership supporting schools'),
    (10, 'P1.F4', 'NC College Connect and direct admission are explicitly named actions under P1.F4'),
    (10, 'P1.F5', 'Automatically offering college spots to 70,000 seniors is a direct postsecondary launch mechanism'),
    (11, 'P4.F2', 'School nutrition and student wellness directly align with health actions under P4.F2'),
    (11, 'P3.F2', 'Farm-to-School partnerships with local agriculture are community/business partnerships'),
    (12, 'P1.F3', 'Advanced manufacturing, healthcare CTE, and Global Innovation Center are rigorous career/academic pathways'),
    (12, 'P1.F4', 'Zoo School experiential learning is a direct example of reimagining the student experience'),
    (12, 'P6.F1', 'Global Innovation Center and Zoo School are clearly innovative school practices'),
    (13, 'P1.F4', 'Student advisor to State Board shaping policy directly reimagines student experience through student voice'),
    (13, 'P1.F3', 'Advocacy on transcript components and class weighting directly relates to equitable access to rigorous pathways'),
    (14, 'P3.F1', 'Parent University video series is a direct family engagement and education initiative'),
    (14, 'P1.F3', 'Content covers CTE and dual language, helping families understand rigorous pathway options'),
    (15, 'P1.F3', 'STEM, robotics, 3D printing, CTE, and AVID are rigorous academic and career pathways'),
    (15, 'P1.F2', 'STEM instruction and digital learning tools (3D printing, robotics) align with elevating teaching through digital learning'),
    (15, 'P2.F2', 'Teacher Advisory Councils represent teacher leadership pathways'),
    (16, 'P1.F3', '550,000+ CTE participants with 98% graduation rate is a direct CTE rigorous pathway outcome'),
    (16, 'P1.F4', 'Career development coordinators and career development plans are a named action under P1.F4'),
    (16, 'P1.F5', 'Work-based learning and workforce readiness directly launch life-ready graduates with durable skills'),
    (17, 'P1.F3', 'Early college with dual enrollment (diploma + associate degree + certificate) is a rigorous advanced pathway'),
    (17, 'P1.F4', 'Internship at a law firm and Teen Court are career development experiences'),
    (17, 'P1.F5', 'Graduating with diploma, associate degree, certificate, and legal internship defines a life-ready graduate'),
    (18, 'P1.F4', 'Student advisory council giving students voice in education policy reimagines student experience through leadership'),
    (18, 'P2.F3', 'Teacher compensation explicitly named as a student priority/advocacy area'),
    (18, 'P4.F2', 'Mental health explicitly named as a student advisory council priority'),
    (19, 'P1.F4', 'Student newspaper and media excellence is an arts/leadership extracurricular under P1.F4'),
    (19, 'P1.F5', 'Distinguished student journalism and UNC pipeline represent durable skills and postsecondary pathways'),
    (20, 'P1.F4', 'College-going culture and experiential learning directly align with reimagining student experience'),
    (20, 'P1.F3', 'Career/college prep pathways are rigorous academic pathways for all students'),
    (20, 'P1.F5', 'College-going culture is a direct mechanism for launching life-ready graduates'),
    (21, 'P1.F3', 'CTE programs and dual enrollment are rigorous career/academic pathways'),
    (21, 'P2.F1', 'UNC Pembroke teacher prep pipeline is a direct educator recruitment/pipeline initiative'),
    (21, 'P1.F5', 'Workforce development with AWS investment and higher ed pathways directly support life-ready graduates'),
    (21, 'P3.F2', 'AWS investment and UNC Pembroke partnership are business/higher-ed community partnerships'),
    (22, 'P1.F3', 'Jr. Chef Competition is a CTE culinary arts pathway with rigorous applied skills'),
    (22, 'P4.F2', 'Creating nutritious school lunches with local produce directly supports school-based health and nutrition'),
    (23, 'P1.F5', 'Portrait of a Graduate skills and civic engagement are durable skills for life readiness'),
    (23, 'P4.F2', 'Physical education bike safety unit directly aligns with physical activity promotion under P4.F2'),
    (23, 'P1.F1', 'Cross-grade peer mentorship in elementary school aligns with collaborative early learning approaches'),
    (24, 'P1.F3', 'CTE at Watauga and dual language immersion are rigorous pathways'),
    (24, 'P2.F1', 'Teacher prep partnership with Appalachian State is a direct teacher pipeline initiative'),
    (24, 'P3.F2', 'Appalachian State teacher prep and community rebuilding after Helene are PSU-community partnerships'),
    (25, 'P2.F4', 'Teachers/Principals of the Year highlights are the named recognition actions under P2.F4'),
    (25, 'P1.F1', 'Early literacy is explicitly mentioned as a point of pride'),
    (25, 'P1.F2', 'STEM and arts integration represent elevated teaching and learning approaches'),
    (25, 'P1.F4', 'Student belonging, arts integration, and STEM represent reimagined student experiences'),
    (26, 'P2.F4', 'Educators sharing resolutions for equity and advocacy directly elevates educator voice and professional pride'),
    (26, 'P8.F1', 'Educators articulating advocacy resolutions is a direct example of building advocacy voices'),
    (27, 'P4.F2', 'School nutrition serving 850,000+ students directly supports student health'),
    (27, 'P3.F2', 'Boys and Girls Clubs, food banks, and YMCAs are explicitly named community partners'),
    (28, 'P1.F2', 'Place-based, inquiry-driven history instruction is an elevated teaching approach'),
    (28, 'P1.F5', 'Civic engagement and service learning are named actions under P1.F5'),
    (28, 'P3.F2', 'Place-based instruction using local civil rights stories is an explicit classroom-community partnership'),
    (28, 'P2.F4', 'National History Teacher recognition elevates and celebrates the profession'),
    (29, 'P2.F1', 'Alternative pathways and grow-your-own program are named teacher pipeline actions under P2.F1'),
    (29, 'P2.F2', 'Bus driver to EC teacher is a literal career pathway within education'),
    (29, 'P1.F3', 'EC education directly relates to equitable services for all students'),
    (30, 'P1.F3', 'Charter schools, early college, CTE with 160+ credentials are rigorous educational pathways'),
    (30, 'P1.F4', 'Helping families find the right school fit across diverse options reimagines the student experience'),
    (30, 'P3.F1', 'Campaign explicitly targets families to help them navigate educational options'),
]

# Write CSV
with open('data/blog_focus_area_matches_draft.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['BlogNum', 'StoryTitle', 'StoryURL', 'StoryPublishDate', 'StoryCounty',
                     'FocusAreaID', 'FocusAreaName', 'PillarID', 'PillarName', 'MatchRationale'])
    for blog_num, fa_id, rationale in matches:
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

print(f'Wrote {len(matches)} matches to data/blog_focus_area_matches_draft.csv')

# Coverage stats
fa_counts = Counter(fa_id for _, fa_id, _ in matches)
blog_counts = Counter(bn for bn, _, _ in matches)
all_fas = set(fa_names.keys())
matched_fas = set(fa_counts.keys())
unmatched = all_fas - matched_fas

print(f'\nFocus areas with matches: {len(matched_fas)}/26')
print(f'Focus areas WITHOUT matches ({len(unmatched)}):')
for fa in sorted(unmatched):
    print(f'  {fa}: {fa_names[fa]}')

print(f'\nBlogs with matches: {len(blog_counts)}/30')
orphaned = set(range(1, 31)) - set(blog_counts.keys())
if orphaned:
    print(f'Orphaned blogs: {sorted(orphaned)}')
else:
    print('No orphaned blogs - all 30 have at least one match')

print('\nFocus area match counts:')
for fa in sorted(fa_names.keys()):
    count = fa_counts.get(fa, 0)
    bar = '#' * count
    print(f'  {fa} ({fa_names[fa][:40]:40s}): {count:2d} {bar}')
