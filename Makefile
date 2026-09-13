.PHONY: render validate update-rules

render:
	python3 scripts/render_config.py

validate:
	python3 scripts/validate_config.py

update-rules:
	python3 scripts/update_remote_rules.py

