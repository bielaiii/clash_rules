.PHONY: render validate test-extension update-rules

render:
	python3 scripts/render_config.py

validate: test-extension
	python3 scripts/validate_config.py

test-extension:
	node scripts/test_global_extension.js

update-rules:
	python3 scripts/update_remote_rules.py
