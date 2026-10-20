# MedAssist AI - Test and Performance Report

Total: 25 | Passed: 25 | Failed: 0

| Test | Result | Time (s) |
|---|---|---|
| test_root | PASSED | 0.01 |
| test_health | PASSED | 0.0 |
| test_ask_requires_auth | PASSED | 0.0 |
| test_history_requires_auth | PASSED | 0.01 |
| test_admin_requires_auth | PASSED | 0.0 |
| test_login_wrong_password | PASSED | 0.06 |
| test_register_duplicate_rejected | PASSED | 0.07 |
| test_login_success_returns_token | PASSED | 0.25 |
| test_login_wrong_password | PASSED | 0.27 |
| test_protected_get_routes_require_login[/history] | PASSED | 0.0 |
| test_protected_get_routes_require_login[/bookmarks] | PASSED | 0.0 |
| test_protected_get_routes_require_login[/admin/documents] | PASSED | 0.0 |
| test_protected_get_routes_require_login[/admin/analytics] | PASSED | 0.0 |
| test_ask_requires_login | PASSED | 0.0 |
| test_ask_image_requires_login | PASSED | 0.0 |
| test_non_admin_blocked_from_admin_routes | PASSED | 0.18 |
| test_admin_list_documents_shape | PASSED | 0.13 |
| test_admin_rejects_non_pdf_upload | PASSED | 0.07 |
| test_corrupt_pdf_marked_failed_then_removed | PASSED | 0.59 |
| test_ask_returns_evidence_structure_and_is_fast | PASSED | 1.92 |
| test_off_topic_question_is_not_grounded | PASSED | 0.88 |
| test_emergency_question_gets_safety_notice | PASSED | 3.29 |
| test_ask_rejects_empty_body | PASSED | 0.07 |
| test_image_endpoint_rejects_non_image | PASSED | 0.06 |
| test_chat_flow_history_bookmark_feedback_export_delete | PASSED | 3.35 |