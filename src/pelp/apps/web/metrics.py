from prometheus_client import Gauge, Counter

users_total = Gauge('pelp_users_total', 'Total number of users')
users_learners = Gauge('pelp_users_learners', 'Total number of users with learner role')
users_instructors = Gauge('pelp_users_instructors', 'Total number of users with instructor privileges')
users_admins = Gauge('pelp_users_admins', 'Total number of users with administration rights')

submissions_total = Gauge('pelp_submissions_total', 'Total number of submissions')
submissions_learners = Gauge('pelp_submissions_learners', 'Total number of submissions by learners')
submissions_execution = Gauge('pelp_submissions_execution', 'Total number of submissions in execution status')
submissions_execution_limit = Gauge('pelp_submissions_execution_limit', 'Limit of submissions in execution')
submissions_status = Gauge('pelp_submissions_status', 'Number of submissions by status', ['status'])

activity_num_learners = Gauge('pelp_activity_num_learners', 'Number of learners', ['semester', 'course', 'activity'])
activity_num_learners_with_submissions = Gauge('pelp_activity_num_learners_with_submissions', 'Number of learners with submissons', ['semester', 'course', 'activity'])
activity_num_submissions = Gauge('pelp_activity_num_submissions', 'Number of Submissions', ['semester', 'course', 'activity'])

activity_score_np = Gauge('pelp_activity_score_np', 'Number of learners with NP score', ['semester', 'course', 'activity'])
activity_score_a = Gauge('pelp_activity_score_a', 'Number of learners with A score', ['semester', 'course', 'activity'])
activity_score_b = Gauge('pelp_activity_score_b', 'Number of learners with B score', ['semester', 'course', 'activity'])
activity_score_cp = Gauge('pelp_activity_score_cp', 'Number of learners with C+ score', ['semester', 'course', 'activity'])
activity_score_cm = Gauge('pelp_activity_score_cm', 'Number of learners with C- score', ['semester', 'course', 'activity'])
activity_score_d = Gauge('pelp_activity_score_d', 'Number of learners with D score', ['semester', 'course', 'activity'])
activity_score = Gauge('pelp_activity_score', 'Number of learners by score', ['semester', 'course', 'activity', 'score'])

activity_qualification_np = Gauge('pelp_activity_qualification_np', 'Number of learners with NP qualification', ['semester', 'course', 'activity'])
activity_qualification_a = Gauge('pelp_activity_qualification_a', 'Number of learners with A qualification', ['semester', 'course', 'activity'])
activity_qualification_b = Gauge('pelp_activity_qualification_b', 'Number of learners with B qualification', ['semester', 'course', 'activity'])
activity_qualification_cp = Gauge('pelp_activity_qualification_cp', 'Number of learners with C+ qualification', ['semester', 'course', 'activity'])
activity_qualification_cm = Gauge('pelp_activity_qualification_cm', 'Number of learners with C- qualification', ['semester', 'course', 'activity'])
activity_qualification_d = Gauge('pelp_activity_qualification_d', 'Number of learners with D qualification', ['semester', 'course', 'activity'])
activity_qualification_pending = Gauge('pelp_activity_qualification_pending', 'Number of learners with pending qualification', ['semester', 'course', 'activity'])
activity_qualification = Gauge('pelp_activity_qualification', 'Number of learners by qualification', ['semester', 'course', 'activity', 'qualification'])

faq_total = Gauge('pelp_faq_total', 'Number of FAQs')
faq_public_total = Gauge('pelp_faq_public_total', 'Number of public FAQs')
faq_rated_total = Gauge('pelp_faq_rated_total', 'Number of rated FAQs')
faq_rated_total_avg = Gauge('pelp_faq_rated_total_avg', 'Total rating average of rated FAQs')
