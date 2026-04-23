.PHONY: enable-service disable-service start-service stop-service restart-service service-status

enable-service:
	@sudo systemctl enable worktime.service

disable-service:
	@sudo systemctl disable worktime.service

start-service:
	@sudo systemctl start worktime.service

stop-service:
	@sudo systemctl stop worktime.service

restart-service:
	@sudo systemctl restart worktime.service

service-status:
	@sudo systemctl status worktime.service | grep -E "Active:" | \
	sed -E "s/active \(running\)/\x1b[1;32m&\x1b[0m/" | \
	sed -E "s/inactive \(dead\)/\x1b[1;31m&\x1b[0m/"
