odoo.define('menu.CustomNotification', function (require) {
    "use strict";

    const WebClient = require('web.WebClient');
    const AbstractWebClient = WebClient.include({
        show_custom_notifications: function() {
            // Logic lấy thông báo và hiển thị trên chuông
            this._rpc({
                model: 'mail.activity',
                method: 'search_read',
                args: [['&', ['user_id', '=', this.session.uid], ['activity_type_id', '=', 'mail.mail_activity_data_todo']]],
                fields: ['activity_type_id', 'summary', 'note', 'date_deadline']
            }).then(function (notifications) {
                const $notificationDropdown = $('#notification-dropdown');
                $notificationDropdown.empty();

                if (notifications.length) {
                    notifications.forEach(notification => {
                        const notificationItem = `
                            <div style="padding: 10px; border-bottom: 1px solid #eee;">
                                <strong>${notification.summary}</strong>
                                <p style="margin: 0; color: #555;">${notification.note}</p>
                                <span style="font-size: 0.8em; color: #888;">${notification.date_deadline}</span>
                            </div>`;
                        $notificationDropdown.append(notificationItem);
                    });
                } else {
                    $notificationDropdown.append('<div style="padding: 10px; text-align: center; color: #888;">No notifications</div>');
                }
            });
        },

        start: function() {
            this._super.apply(this, arguments);
            this.show_custom_notifications();
        }
    });

    return AbstractWebClient;
});
