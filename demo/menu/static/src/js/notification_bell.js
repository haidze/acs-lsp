odoo.define('menu.notification_bell', function (require) {
    "use strict";

    const { Component, hooks } = owl;
    const { useState } = hooks;
    const AbstractAction = require('web.AbstractAction');
    const rpc = require('web.rpc');

    const NotificationBell = AbstractAction.extend({
        template: 'NotificationBellTemplate',
        events: {
            'click .fa-bell': '_onBellClick',
        },
        init: function (parent, action) {
            this._super(parent, action);
            this.state = useState({
                notifications: [],
                showDropdown: false,
            });
        },
        _onBellClick: function () {
            this.state.showDropdown = !this.state.showDropdown;
            if (this.state.showDropdown) {
                this._fetchNotifications();
            }
        },
        _fetchNotifications: function () {
            const self = this;
            rpc.query({
                model: 'coming.plan',
                method: 'get_notifications',
                args: [],
            }).then(function (notifications) {
                self.state.notifications = notifications;
                self.render(); // Render lại component sau khi có thông báo mới
            });
        },
    });

    return NotificationBell;
});
