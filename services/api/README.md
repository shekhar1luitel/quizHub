# Loksewa Quiz Hub API

This document lists the available backend REST endpoints exposed by the Loksewa Quiz Hub service. All routes are served under the `/api` prefix by the FastAPI application defined in `app/main.py`.

## Endpoints

| HTTP Method | Path | Module | Handler | Description |
| --- | --- | --- | --- | --- |
| GET | `/api/health` | `health.py` | `health` | - |
| POST | `/api/admin/bulk-import/commit` | `admin.py` | `commit_bulk_import` | - |
| GET | `/api/admin/bulk-import/export` | `admin.py` | `download_bulk_import_export` | - |
| POST | `/api/admin/bulk-import/preview` | `admin.py` | `preview_bulk_import` | - |
| GET | `/api/admin/bulk-import/template` | `admin.py` | `download_bulk_import_template_route` | - |
| GET | `/api/admin/config/mail` | `admin.py` | `get_mail_config` | - |
| PUT | `/api/admin/config/mail` | `admin.py` | `update_mail_config` | - |
| POST | `/api/admin/email/dispatch` | `admin.py` | `dispatch_email_events` | - |
| POST | `/api/admin/notifications` | `admin.py` | `create_admin_notification` | - |
| GET | `/api/admin/overview` | `admin.py` | `get_admin_overview` | - |
| GET | `/api/admin/users` | `admin.py` | `list_admin_users` | - |
| POST | `/api/admin/users` | `admin.py` | `create_admin_user` | - |
| PUT | `/api/admin/users/{user_id}/status` | `admin.py` | `update_admin_user_status` | - |
| GET | `/api/analytics/overview` | `analytics.py` | `get_analytics_overview` | - |
| POST | `/api/attempts/` | `attempts.py` | `submit_attempt` | - |
| GET | `/api/attempts/history` | `attempts.py` | `list_attempt_history` | - |
| GET | `/api/attempts/{attempt_id}` | `attempts.py` | `get_attempt` | - |
| POST | `/api/auth/login` | `auth.py` | `login` | - |
| POST | `/api/auth/register` | `auth.py` | `register` | - |
| POST | `/api/auth/resend-verification` | `auth.py` | `resend_verification` | - |
| POST | `/api/auth/verify-email` | `auth.py` | `verify_email` | - |
| GET | `/api/bookmarks/` | `bookmarks.py` | `list_bookmarks` | - |
| POST | `/api/bookmarks/` | `bookmarks.py` | `create_bookmark` | - |
| GET | `/api/bookmarks/ids` | `bookmarks.py` | `list_bookmarked_question_ids` | - |
| DELETE | `/api/bookmarks/{question_id}` | `bookmarks.py` | `delete_bookmark` | - |
| GET | `/api/categories/` | `categories.py` | `list_categories` | - |
| POST | `/api/categories/` | `categories.py` | `create_category` | - |
| DELETE | `/api/categories/{category_id}` | `categories.py` | `delete_category` | - |
| PUT | `/api/categories/{category_id}` | `categories.py` | `update_category` | - |
| GET | `/api/dashboard/summary` | `dashboard.py` | `get_dashboard_summary` | - |
| GET | `/api/notifications` | `notifications.py` | `list_notifications` | - |
| POST | `/api/notifications/read-all` | `notifications.py` | `mark_all_notifications_read` | - |
| POST | `/api/notifications/{notification_id}/read` | `notifications.py` | `mark_notification_read` | - |
| GET | `/api/organizations` | `organizations.py` | `list_organizations` | - |
| POST | `/api/organizations` | `organizations.py` | `create_organization` | - |
| POST | `/api/organizations/enroll` | `organizations.py` | `enroll_current_user` | - |
| PATCH | `/api/organizations/{organization_id}` | `organizations.py` | `update_organization` | - |
| POST | `/api/organizations/{organization_id}/enroll-tokens` | `organizations.py` | `create_enroll_token` | - |
| GET | `/api/organizations/{organization_id}/members` | `organizations.py` | `list_organization_members` | - |
| GET | `/api/practice/bookmarks` | `practice.py` | `get_bookmark_revision_set` | - |
| GET | `/api/practice/categories` | `practice.py` | `list_practice_categories` | - |
| GET | `/api/practice/categories/{slug}` | `practice.py` | `get_practice_category` | - |
| GET | `/api/public/home` | `public.py` | `get_public_home` | - |
| GET | `/api/questions/` | `questions.py` | `list_questions` | - |
| POST | `/api/questions/` | `questions.py` | `create_question` | - |
| DELETE | `/api/questions/{question_id}` | `questions.py` | `delete_question` | - |
| GET | `/api/questions/{question_id}` | `questions.py` | `get_question` | - |
| PUT | `/api/questions/{question_id}` | `questions.py` | `update_question` | - |
| GET | `/api/quizzes/` | `quizzes.py` | `list_quizzes` | - |
| POST | `/api/quizzes/` | `quizzes.py` | `create_quiz` | - |
| DELETE | `/api/quizzes/{quiz_id}` | `quizzes.py` | `delete_quiz` | - |
| GET | `/api/quizzes/{quiz_id}` | `quizzes.py` | `get_quiz` | - |
| PUT | `/api/quizzes/{quiz_id}` | `quizzes.py` | `update_quiz` | - |
| GET | `/api/subjects/` | `subjects.py` | `list_subjects` | - |
| POST | `/api/subjects/` | `subjects.py` | `create_subject` | - |
| DELETE | `/api/subjects/{subject_id}` | `subjects.py` | `delete_subject` | - |
| PUT | `/api/subjects/{subject_id}` | `subjects.py` | `update_subject` | - |
| GET | `/api/subjects/{subject_id}/topics` | `subjects.py` | `list_topics` | - |
| POST | `/api/subjects/{subject_id}/topics` | `subjects.py` | `create_topic` | - |
| DELETE | `/api/subjects/{subject_id}/topics/{topic_id}` | `subjects.py` | `delete_topic` | - |
| PUT | `/api/subjects/{subject_id}/topics/{topic_id}` | `subjects.py` | `update_topic` | - |
| GET | `/api/users/me` | `users.py` | `me` | - |
| PATCH | `/api/users/me` | `users.py` | `update_me` | - |

