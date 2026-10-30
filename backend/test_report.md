# MedAssist AI - Test and Performance Report

Total: 25 | Passed: 25 | Failed: 0

| Test | Result | Time (s) |
|---|---|---|
| test_root | PASSED | 0.02 |
| test_health | PASSED | 0.01 |
| test_ask_requires_auth | PASSED | 0.01 |
| test_history_requires_auth | PASSED | 0.01 |
| test_admin_requires_auth | PASSED | 0.01 |
| test_login_wrong_password | PASSED | 0.04 |
| test_register_duplicate_rejected | PASSED | 0.04 |
| test_login_success_returns_token | PASSED | 0.66 |
| test_login_wrong_password | PASSED | 0.64 |
| test_protected_get_routes_require_login[/history] | PASSED | 0.01 |
| test_protected_get_routes_require_login[/bookmarks] | PASSED | 0.01 |
| test_protected_get_routes_require_login[/admin/documents] | PASSED | 0.01 |
| test_protected_get_routes_require_login[/admin/analytics] | PASSED | 0.01 |
| test_ask_requires_login | PASSED | 0.01 |
| test_ask_image_requires_login | PASSED | 0.01 |
| test_non_admin_blocked_from_admin_routes | PASSED | 0.16 |
| test_admin_list_documents_shape | PASSED | 0.09 |
| test_admin_rejects_non_pdf_upload | PASSED | 0.04 |
| test_corrupt_pdf_marked_failed_then_removed | PASSED | 0.37 |
| test_ask_returns_evidence_structure_and_is_fast | PASSED | 1.79 |
| test_off_topic_question_is_not_grounded | PASSED | 0.83 |
| test_emergency_question_gets_safety_notice | PASSED | 2.86 |
| test_ask_rejects_empty_body | PASSED | 0.04 |
| test_image_endpoint_rejects_non_image | PASSED | 0.04 |
| test_chat_flow_history_bookmark_feedback_export_delete | PASSED | 3.0 |