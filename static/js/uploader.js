// © Copyright 2017. All Rights Reserved.
// Jure Bernava Prah

// UploaderJS singleton and namespace
if (typeof window.UploaderJS !== 'object') {

    window.UploaderJS = (function () {
        'use strict';

        var UPLOADERJS_HOST = 'uploaderjs.com'
            , UPLOADERJS_SCHEME = 'https://'
            , VERSION_API = 'v1'
            , _scripts = []
            , _on_loading_scripts = []
            , _completed_loading_scripts = []
            , _drawers = []
            , _uploaderjs_initialized = false;


        var Log = function () {

        };
        Log.error = function (message) {
            Events.logging('Error', message);
            console.error(message);
        };
        Log.warn = function (message) {
            Events.logging('Warn', message);
            console.warn(message);
        };
        Log.log = function (message) {
            console.log(message);
        };
        Log.debug = function (message) {
            if (location.hostname === 'uploaderjs.local') {
                console.debug(message);
            }

        };

        var Events = function () {

        };

        Events.pageview = function () {
            window.ga('uploaderjs.send', 'pageview');
        };
        Events.logging = function (action, value) {
            Utilities.event('Error', action, value);
        };
        Events.drawer = function (action, value) {
            Utilities.event('Drawer', action, value);
        };
        Events.file = function (action, value) {
            Utilities.event('File', action, value);
        };

        var Utilities = function () {
        };
        Utilities.event = function (category, action, value) {

            if (window.ga) {

                var fields = {
                    hitType: 'event',
                    eventCategory: category,
                    eventAction: action
                };
                if (value) {
                    if (typeof value === 'string') {
                        fields['eventLabel'] = value;
                    } else {
                        fields['eventValue'] = value;
                    }
                }

                window.ga('uploaderjs.send', fields);
            }


        };
        Utilities.call = function (after, callback) {
            setTimeout(callback, after);
        };
        Utilities.correctUrl = function () {
            if (location.hostname === 'localhost' || location.hostname === '127.0.0.1' || location.hostname === 'uploaderjs.local') {
                UPLOADERJS_HOST = location.hostname + ':8080';
                UPLOADERJS_SCHEME = '//';
            }
        };


        Utilities.getKeys = function (obj) {
            var arr = [],
                key;
            for (key in obj) {
                if (obj.hasOwnProperty(key)) {
                    arr.push(key);
                }
            }
            return arr;
        };

        Utilities.objectLength = function (obj) {
            return this.getKeys(obj).length;
        };
        Utilities.getParameters = function (queryString) {
            var params = Utilities.parseQuery(window.location.search.substring(1));
            return Utilities.parseQuery(queryString, params);
        };
        Utilities.createQuery = function (obj) {
            if (!obj) return '';
            var str = [];
            for (var p in obj)
                if (obj.hasOwnProperty(p)) {
                    str.push(window.encodeURIComponent(p) + "=" + window.encodeURIComponent(obj[p]));
                }
            return str.join("&");

        };
        Utilities.parseQuery = function (str, query) {
            if (!query) query = {};
            if (typeof str !== "string" || str.length === 0) return query;
            var s = str.split("&");
            var s_length = s.length;
            var bit, first, second;
            for (var i = 0; i < s_length; i++) {

                if (-1 === s[i].indexOf('=')) {
                    first = window.decodeURIComponent(bit[0]);
                    second = true;
                } else {
                    bit = s[i].split("=");
                    first = window.decodeURIComponent(bit[0]);
                    if (first.length === 0) continue;
                    if (bit.length < 2) {
                        second = true;
                    } else {
                        second = window.decodeURIComponent(bit[1]);
                    }
                }

                if (typeof query[first] === "undefined") query[first] = second;
                else if (query[first] instanceof Array) query[first].push(second);
                else query[first] = [query[first], second];
            }
            return query;
        };
        Utilities.addEvent = function (ele, event, callback) {

            if (ele.addEventListener) {
                ele.addEventListener(event, callback, false);  //Modern browsers
            } else if (ele.attachEvent) {
                ele.attachEvent('on' + event, callback);            //Old IE
            }
        };
        Utilities.loadHeadElements = function (type, success) {

            if (_scripts.length === 0) {
                success();
                return;
            }

            var head = document.getElementsByTagName('head')[0];

            if (!head) {
                Log.error('No head found.')
            }

            for (var element in _scripts) {

                if (!_scripts.hasOwnProperty(element)) {
                    continue;
                }

                if (!_scripts[element]['check']) {
                    continue;
                }


                var url = _scripts[element]['script'];

                if (url in _completed_loading_scripts || url in _on_loading_scripts) {
                    continue;
                }

                if (url[0] === '/') {

                    url = UPLOADERJS_SCHEME + UPLOADERJS_HOST + url;
                }

                _on_loading_scripts.push(url);

                var script = document.createElement(type);

                if (type === 'script') {
                    script.type = 'text/javascript';
                    script.src = url;
                    // Attach handlers for all browsers
                    script.onload = script.onreadystatechange = function () {
                        if ((!this.readyState || this.readyState === 'loaded' || this.readyState === 'complete')) {
                            Log.debug('Completed load ' + type + ': ' + this.src);
                            _completed_loading_scripts.push(this.src);
                            // callback function provided as param
                            if (_completed_loading_scripts.length === _on_loading_scripts.length) {


                                Log.debug('Completed all load ' + type + '.');

                                if (typeof success === 'function') {
                                    success();
                                }


                                this.onload = this.onreadystatechange = null;
                                //head.removeChild(this);
                            }
                        }
                    };
                }

                /*
                if (type === 'link') {
                    script.setAttribute('rel', 'stylesheet');
                    script.setAttribute("type", "text/css");
                    script.setAttribute("href", url);
                    script.onload = script.onreadystatechange = function () {
                        _loaded.push(this.src);
                        Log.debug('Completed load ' + type + ': ' + this.href);
                        if (_loaded.length === urls.length) {
                            Log.debug('Completed all load ' + type + '.');
                            _loaded = null;
                            urls = null;
                            if (typeof success === 'function') {
                                success();
                            }
                            this.onload = this.onreadystatechange = null;
                        }
                    }
                }*/

                head.appendChild(script);
            }
        };


        Utilities.polyfill = function () {

            window.decodeURIComponent = window.decodeURIComponent || window.unescape;
            window.encodeURIComponent = window.encodeURIComponent || window.escape;

            if (!document.getElementsByClassName) {
                document.getElementsByClassName = function (cn) {
                    var allT = document.getElementsByTagName('*'), allCN = [], i = 0, a;
                    while (a = allT[i++]) {
                        a.className == cn ? allCN[allCN.length] = a : null;
                    }
                    return allCN
                }
            }

            _scripts.push({
                    'check': !window.JSON || !window.JSON.stringify || !window.JSON.parse,
                    'script': '/static/js/json2.js'
                }
            );


            _scripts.push({
                'check': !window.GoogleAnalyticsObject,
                'script': 'https://www.google-analytics.com/analytics.js'
            });

            // Analytics
            window['GoogleAnalyticsObject'] = 'ga';
            window['ga'] = window['ga'] || function () {
                (window['ga'].q = window['ga'].q || []).push(arguments)
            };
            window['ga'].l = 1 * new Date();
            window.ga('create', 'UA-21002124-30', 'auto', 'uploaderjs');

            if (!Array.prototype.indexOf) {
                Array.prototype.indexOf = function (searchValue, index) {
                    var len = this.length >>> 0;
                    index |= 0;
                    if (index < 0)
                        index = Math.max(len - index, 0);
                    else if (index >= len)
                        return -1;

                    if (searchValue === undefined)
                        do {
                            if (index in this && this[index] === undefined)
                                return index;
                        } while (++index !== len);
                    else
                        do {
                            if (this[index] === searchValue)
                                return index;
                        } while (++index !== len);

                    return -1;
                };
            }

            Utilities.loadHeadElements('script', function () {

                _uploaderjs_initialized = true;

                var to_test = [window.JSON, window.decodeURIComponent, window.encodeURIComponent, Array.prototype.indexOf];
                for (var t in to_test) {
                    if (!to_test.hasOwnProperty(t)) continue;
                    if (!to_test[t])
                        throw 'Browser not compatible. Fallback!';
                }

                for (var _drawer in _drawers) {
                    if (!_drawers.hasOwnProperty(_drawer)) continue;
                    _drawers[_drawer].init();
                }
            });

        };

        var RequestsControl = function () {
        };
        RequestsControl.getKey = function () {
            return JSON.stringify(arguments);
        };
        RequestsControl.data = {};
        RequestsControl.after = 300;
        RequestsControl.remove = function (key) {
            delete this.data[key];
        };
        RequestsControl.exist = function (key) {
            return !!this.data[key];
        };
        RequestsControl.count = function (key) {
            return this.data[key];
        };
        RequestsControl.set = function (key) {
            this.data[key] = 1

        };
        RequestsControl.increment = function (key) {
            if (!this.exist(key))
                this.data[key] = 0;
            this.data[key] += 1;
        };


        var Load = function () {
        };

        Load.request = function (args) {
            var request_args = {
                url: '',
                data: '',
                method: '',
                async: true,
                header: [],
                callback: null,
                drawer: null
            };

            for (var arg in args) {
                if (!args.hasOwnProperty(arg)) continue;
                request_args[arg] = args[arg];
            }

            var key = RequestsControl.getKey(request_args.url, request_args.data);
            var xhr = Load.get_correct_xhr(request_args.url);
            xhr.onreadystatechange = function () {

                if (this.readyState === 4) {

                    try {
                        var data = null;
                        data = JSON.parse(xhr.responseText);
                    } catch (e) {
                        RequestsControl.increment(key);
                        Log.error('Error decoding json.');
                        Load.request(args);
                        return;
                    }

                }

                if (this.readyState === 4 && this.status === 200) {
                    Log.debug('Successful response ' + request_args.url + '.');
                    if (typeof request_args.callback === 'function') {
                        request_args.callback(data);
                    }
                    RequestsControl.remove(key);
                    return;
                }

                if (this.readyState === 4 && this.status >= 400 && this.status < 500) {

                    if (data['feedback']) {
                        if (typeof request_args.callback === 'function') {
                            request_args.callback(data);
                        }
                        RequestsControl.remove(key);
                        return;
                    }

                    var message = data['error'] || this.statusText;

                    request_args.drawer.dI.draw(DrawerTemplate.draw_error, message, false);
                    Log.error('Error: ' + message);
                    RequestsControl.remove(key);
                    return

                }


                if (this.readyState === 4 && this.status >= 500) {
                    RequestsControl.increment(key);
                    Log.error('Error: ' + this.statusText);
                    Load.request(args);
                }
            };

            xhr.open(request_args.method, request_args.url, request_args.async);
            //Send the proper header information along with the request
            if (request_args.headers) {
                for (var h in request_args.headers) {
                    if (!request_args.headers.hasOwnProperty(h)) continue;
                    Log.debug('Apply header: ' + h);
                    xhr.setRequestHeader(h, request_args.headers[h]);
                }

            }

            if (RequestsControl.exist(key)) {
                var count = RequestsControl.count(key);
                var ms = count * RequestsControl.after;
                Log.warn('Slow request (' + request_args.url + ') now ' + count + ' times. Will be sent again in ' + ms + 'ms.');
                Utilities.call(ms, function () {
                    xhr.send(request_args.data);
                })
            } else {
                xhr.send(request_args.data);
            }

        };
        Load.get_correct_xhr = function () {
            var xhr;

            if (typeof XMLHttpRequest !== 'undefined') xhr = new XMLHttpRequest();
            else {
                var versions = ["MSXML2.XmlHttp.5.0",
                    "MSXML2.XmlHttp.4.0",
                    "MSXML2.XmlHttp.3.0",
                    "MSXML2.XmlHttp.2.0",
                    "Microsoft.XmlHttp"];

                for (var i = 0, len = versions.length; i < len; i++) {
                    try {
                        xhr = new ActiveXObject(versions[i]);
                        break;
                    }
                    catch (e) {
                    }
                } // end for
            }
            return xhr;
        };

        Utilities.ajax = function (method, uri, parameters, drawer, callback) {

            parameters['random'] = new Date().getTime() + '' + Math.floor(Math.random() * 9e15);

            parameters = JSON.stringify(parameters);

            var args = {
                url: UPLOADERJS_SCHEME + 'api.' + UPLOADERJS_HOST + uri,
                data: parameters,
                method: method,
                async: true,
                headers: {
                    'content-type': "application/json",
                    'Authorization': "Bearer " + drawer.params['token']
                    //'uploaderjs-request-from': drawer.params['request_from']
                },
                callback: callback,
                drawer: drawer
            };

            Load.request(args);
        };

        var DrawerUtilities = function () {
        };
        DrawerUtilities._script = function () {
            //var _js = ['static/vendor/bootstrap/js/bootstrap.min.js',];
            var _js = [];
            var elements = '';
            for (var i = 0; i < _js.length; i++) {
                elements += '<script src="' + _js[i] + '"></script>';
            }
            return elements;
        };
        DrawerUtilities._css = function () {
            var _css = ['https://fonts.googleapis.com/css?family=Open+Sans:300,400,600,700,800%7CShadows+Into+Light',
                'static/vendor/bootstrap/css/bootstrap.min.css',
                'static/vendor/font-awesome/css/font-awesome.min.css',
                'static/css/theme.css',
                'static/css/theme-elements.css',
                'static/css/skins/default.css',
                'static/css/custom.css'
            ];
            var elements = '';
            for (var i = 0; i < _css.length; i++) {

                elements += '<link rel="stylesheet" href="' + _css[i] + '"/>';
            }
            return elements;

        };
        DrawerUtilities.check_form = function (position) {
            var node = position;
            while (node.nodeName !== "FORM" && node.parentNode) {
                node = node.parentNode;
            }
            return node.nodeName === "FORM" ? node : false;

        };
        DrawerUtilities.setAttributes = function (element, attributes) {
            if (typeof attributes === 'object') {
                for (var att in attributes) {
                    if (!attributes.hasOwnProperty(att)) continue;
                    if (att === 'text') {
                        element.innerHTML = attributes[att];
                    } else if (att.substring(0, 2) === 'on') {
                        element[att] = attributes[att];
                    } else {
                        element.setAttribute(att, attributes[att]);
                    }
                }
            }
            return element;
        };

        var DrawerTemplate = function () {

        };

        DrawerTemplate.draw_skeleton = function () {

            var div = this._element('div', {'style': ''});
            this.drawer.position.parentNode.insertBefore(div, this.drawer.position.nextSibling);

            this.iframe = this._element('iframe', {
                'frameborder': 'no',
                'scrolling': 'no',
                'marginheight': '0',
                'marginwidth': '0',
                'width': '100%',
                'height': '100%'
                //,
                //'src' : 'about:blank'
            }, div);


            var footer = '<div class="row mt-xs pull-right"><div class="col-xs-12 "><small>© Copyright 2017. All Rights Reserved. <a href="' + UPLOADERJS_SCHEME + UPLOADERJS_HOST + '">UploaderJS.com</a></small></div></div>';
            var section = '<section><div class="row"><div class="col-xs-12"><div id="real_body"></div></div></div>' + footer + '</section>';

            var html = '<html class="boxed"><head><base href="' + this.base_url + '" />' + DrawerUtilities._css() + '</head><body id="body"><div role="main" class="main mt20" id="home">' + section + '</div> ' + DrawerUtilities._script() + ' </body></html>';
            this.iframe.contentWindow.document.open();
            this.iframe.contentWindow.document.write(html);
            this.iframe.contentWindow.document.close();

            var real_body = this._get_by_id('real_body');

            var upper_row = this._element('div', {'class': 'row center mb-xs'}, real_body);
            this.upper_section = this._element('div', {'class': 'col-md-12'}, upper_row);

            var body_row = this._element('div', {'class': 'row '}, real_body);
            var body_col = this._element('div', {'class': 'col-md-12'}, body_row);

            var call_action = this._element('section', {'class': 'call-to-action with-borders button-centered mb-xs pb-xl pl-xl pr-xl'}, body_col);

            this.body_section = this._element('div', {'class': "call-to-action-content ajax-box-loading pt-xs"}, call_action);

            var bottom_row = this._element('div', {'class': 'row mt-xs center'}, real_body);
            this.bottom_section = this._element('div', {'class': 'col-md-12'}, bottom_row);


            var self = this;
            var reset_interval = function () {
                var el = self._get_by_id('home');
                self.iframe.style.height = el.scrollHeight + "px";
            };
            reset_interval();
            setInterval(reset_interval, 350);

        };
        DrawerTemplate.draw_loading = function (to_element) {
            to_element = to_element || this.body_section;
            var d = this._element('div', {}, to_element);
            var bounce = this._element('div', {class: 'bounce-loader'}, d);
            this._element('div', {class: 'bounce1'}, bounce);
            this._element('div', {class: 'bounce2'}, bounce);
            this._element('div', {class: 'bounce3'}, bounce);


        };

        DrawerTemplate.draw_error = function (error, can_restart) {

            var row = this._element('div', {class: 'row'}, this.body_section);
            var col12 = this._element('div', {class: 'col-md-12'}, row);

            var alert = this._element('div', {class: 'alert'}, col12);
            this._element('h3', {text: '<span class="fa fa-frown-o"></span> There are some error:'}, alert);
            this._element('br', {}, alert);
            this._element('h6', {text: error}, alert);
            if (can_restart) {
                var self = this;
                this._element('button', {
                    class: 'btn btn-warn',
                    text: 'Restart process',
                    onclick: function (event) {
                        event.preventDefault();
                        self.draw(DrawerTemplate.draw_question);
                    }
                }, alert);


            } else {
                //this._element('p', {text: 'We have sent notification of error to owner of website. Retry later..'}, alert);
            }

        };

        DrawerTemplate.draw_qrcode = function (attach_to) {
            this._element('h5', {text: 'qrCode:'}, attach_to);
            this._element('img', {
                src: this.drawer.params['form_qrcode_url'],
                alt: 'Url: ' + this.drawer.params['form_url'],
                width: 128,
                height: 128
            }, attach_to);
            this._element('br', {}, attach_to);
            this._element('small', {text: 'Scan it and open url'}, attach_to);
        };

        DrawerTemplate.draw_sms = function (attach_to) {

            var self = this;
            this._element('h5', {text: 'SMS:'}, attach_to);
            var row_telephone = this._element('div', {'class': 'row'}, attach_to);
            var col12_telephone = this._element('div', {'class': 'col-xs-12'}, row_telephone);

            var form_telephone = this._element('form', {
                onsubmit: function (event) {
                    event.preventDefault();

                    self.drawer._send_link_to_number(tel_input, tel_button);
                }
            }, col12_telephone);

            var input_group_telephone = this._element('div', {'class': 'input-group'}, form_telephone);

            var tel_input = this._element('input', {
                'class': "form-control",
                'placeholder': "+39 3332221116",
                //'readonly': 'readonly',
                'type': 'tel',
                'value': ''
            }, input_group_telephone);

            var span_telephone = this._element('span', {'class': 'input-group-btn'}, input_group_telephone);
            var tel_button = this._element('input', {
                type: 'submit',
                value: 'Send',
                'class': 'btn btn-success'
            }, span_telephone);

            this._element('small', {text: "<b>Attention:</b> Normal SMS rates apply. We will use this only sent you your link."}, form_telephone);
            this._element('br', {}, form_telephone);
            this._element('small', {id: 'feedback_sms'}, form_telephone);
        };

        DrawerTemplate.draw_telegram = function (attach_to) {
            var self = this;

            var testimonial = this._element('div', {'class': "testimonial testimonial-primary"}, attach_to);
            var testimonial_author = this._element('div', {'class': "testimonial-author"}, testimonial);
            var thumb = this._element('div', {'class': 'testimonial-author-thumbnail img-thumbnail'}, testimonial_author);
            this._element('img', {src: this.drawer.params['telegram_logo_url']}, thumb);

            this._element('p', {text: '<strong>Telegram</strong><span>UploaderJSBot</span>'}, testimonial_author);


        };

        DrawerTemplate.draw_messenger = function (attach_to) {
            var self = this;

            var testimonial = this._element('div', {'class': "testimonial testimonial-primary"}, attach_to);
            var testimonial_author = this._element('div', {'class': "testimonial-author"}, testimonial);
            var thumb = this._element('div', {'class': 'testimonial-author-thumbnail img-thumbnail'}, testimonial_author);
            this._element('img', {src: this.drawer.params['messenger_logo_url']}, thumb);

            this._element('p', {text: '<strong>Messenger</strong><span>@UploaderJS</span>'}, testimonial_author);

        };

        DrawerTemplate.draw_unique_link = function () {


            this._element('h3', {text: 'Open URL in browser of your phone.', 'class': "mt-xs"}, this.body_section);

            //<div class="alert alert-success"><h2 class="mb-none">http://r.uploaderjs.local:8080/y6ol</h2></div>
            var alert = this._element('div', {'class': "alert alert-success mt-lg"}, this.body_section);
            this._element('h5', {text: 'Your unique url is:'}, alert);
            this._element('h2', {'class': "mb-none", text: this.drawer.params['form_url']}, alert);
            this._element('hr', {}, this.body_section);
            this._element('p', {text: '<b>Get this url</b> by Scan QrCode, get SMS or use Telegram or Messenger.'}, this.body_section);

            var row_services = this._element('div', {'class': 'row'}, this.body_section);

            var col_sx = this._element('div', {'class': 'col-xs-3'}, row_services);

            var row_xs = this._element('div', {'class': 'row'}, col_sx);
            var col_qrcode = this._element('div', {'class': 'col-xs-12'}, row_xs);

            this.drawer.dI.draw_update(DrawerTemplate.draw_qrcode, col_qrcode);


            // Telephone!
            var col_center = this._element('div', {'class': 'col-xs-5'}, row_services);
            var row_center = this._element('div', {'class': 'row'}, col_center);
            var col_social = this._element('div', {'class': 'col-xs-12'}, row_center);
            this._element('h5', {text: "Social:"}, col_social);
            var row_social = this._element('div', {'class': 'row'}, col_social);
            var col_telegram = this._element('div', {'class': 'col-xs-6'}, row_social);
            this.drawer.dI.draw_update(DrawerTemplate.draw_telegram, col_telegram);
            var col_messenger = this._element('div', {'class': 'col-xs-6'}, row_social);
            this.drawer.dI.draw_update(DrawerTemplate.draw_messenger, col_messenger);
            var col_help = this._element('div', {'class': 'col-xs-12'}, row_center);
            this._element('br', {}, col_help);
            this._element('small', {text: "Your personal token for bot is: <b>" + this.drawer.params['form_token'] + "</b>"}, col_help);

            var col_dx = this._element('div', {'class': 'col-xs-4'}, row_services);
            var row_dx = this._element('div', {'class': 'row'}, col_dx);
            var col_sms = this._element('div', {'class': 'col-xs-12'}, row_dx);
            this.drawer.dI.draw_update(DrawerTemplate.draw_sms, col_sms);


        };
        DrawerTemplate.draw_feedback = function (element, message) {
            var feedback_element = this._get_by_id('feedback_' + element);
            feedback_element.innerHTML = message;

        };

        DrawerTemplate.draw_question = function () {
            var self = this;

            this._element('h5', {
                'class': 'mb-xs',
                'text': 'Use your smartphone to upload files.'
            }, this.body_section);
            this._element('small', {
                'text': 'No app install, only browser use and it\'s free.'
            }, this.body_section);
            this._element('br', {}, this.body_section);
            this._element('input', {
                'type': 'button',
                'class': 'btn btn-primary mt-md',
                'value': 'Start it',
                'onclick': function (event) {

                    event.preventDefault();
                    self.drawer._request_form_id();

                }
            }, this.body_section);

            this._element('br', {}, this.body_section);
            this._element('br', {}, this.body_section);
            this._element('h6', {'text': 'We on UploaderJS.com take a lot to your privacy.'}, this.body_section);
            this._element('small', {
                text: 'Your files will be saved and encrypted in our datacenters and only owner of this form can download and decrypt its. In addition, all your files will be deleted after submit of that form and if that is not happen will be always deleted after 24 hours.'
            }, this.body_section);
        };

        // ###############
        // ## INTERFACES
        // ###############

        var DrawerInterface = function () {
        };
        DrawerInterface.prototype._element = function (ele, attributes, append_to) {
            var _el = document.createElement(ele);
            if (append_to) append_to.appendChild(_el);
            return DrawerUtilities.setAttributes(_el, attributes);
        };
        DrawerInterface.prototype._get_by_class = function (_class) {
            if (!this.iframe.contentWindow.document.getElementsByClassName) {
                this.iframe.contentWindow.document.getElementsByClassName = document.getElementsByClassName;
            }

            return this.iframe.contentWindow.document.getElementsByClassName(_class);
        };
        DrawerInterface.prototype._get_by_id = function (id) {
            return this.iframe.contentWindow.document.getElementById(id);
        };
        DrawerInterface.prototype._delete_by_id = function (id) {

            var _el = this._get_by_id(id);
            if (_el) {
                _el.parentNode.removeChild(_el);
                return;
            }

            _el = document.getElementById(id);
            if (_el) {
                _el.parentNode.removeChild(_el);
            }

        };
        DrawerInterface.prototype._draw_empty_content = function (ele) {
            ele = ele || this.body_section;
            if (ele)
                ele.innerHTML = '';
        };
        DrawerInterface.prototype._draw = function () {
            var args = [];
            Array.prototype.push.apply(args, arguments);
            var what = args.shift();
            if (typeof what === 'function') {
                what.apply(this, args);
            } else {
                throw 'Specific a function using DrawerTemplate.template_name';
            }
        };
        DrawerInterface.prototype.file_section = null;
        DrawerInterface.prototype.body_section = null;
        DrawerInterface.prototype.iframe = null;
        DrawerInterface.prototype.drawer = null;


        DrawerInterface.prototype.draw = function () {
            this._draw_empty_content();
            this._draw.apply(this, arguments);

        };
        DrawerInterface.prototype.draw_update = function () {
            this._draw.apply(this, arguments);
        };

        // ###############
        // ## DRAWER
        // ###############

        var Drawer = function (position, params) {

            params = Utilities.parseQuery(window.location.search.substring(1), params);

            // fill additional parameters
            //params['request_from'] = window.location.href;
            if (!params['token']) {
                params['token'] = window.location.hostname;
            }

            this.params = params;
            this.position = position;

            this.dI = new DrawerInterface();
            this.dI.drawer = this;

            if (!_uploaderjs_initialized) {
                _drawers.push(this);
                return;
            }

            this.init();


        };
        Drawer.prototype.params = {};
        Drawer.prototype.position = null;
        Drawer.prototype.form = null;
        Drawer.prototype.hidden_input = null;
        Drawer.prototype.init = function () {

            this.form = DrawerUtilities.check_form(this.position);
            if (this.form !== false) {
                this.dI.draw(DrawerTemplate.draw_skeleton);
                this.dI.draw(DrawerTemplate.draw_loading);
                Log.debug('Start new form!');
                this.dI.draw(DrawerTemplate.draw_question);
                return;
            }

            Log.debug('No form found. Add script into < form > tag.');
            // TODO: GET LANGUAGE!


        };

        Drawer.prototype._request_form_id = function () {
            var self = this;
            Log.debug('Request new form key...');

            Utilities.ajax('POST', '/' + VERSION_API + '/apps/current/forms', {}, this, function (data) {

                Log.debug('New form_id key: ' + data['form_id'] + ' ');

                for (var key in data) {
                    if (data.hasOwnProperty(key)) {
                        self.params[key] = data[key];
                    }
                }


                if (self.hidden_input) {
                    self.hidden_input.value = data['form_id'];
                } else {
                    self.hidden_input = self.dI._element('input', {
                        name: 'uploaderjs_form_id',
                        type: 'hidden',
                        value: data['form_id']
                    }, self.form);
                }


                self.dI.draw(DrawerTemplate.draw_unique_link);


            });
        };

        Drawer.prototype._send_link_to_number = function (input, button) {
            var self = this;

            var number = input.value;

            if (!number || number.length < 5) {
                return;
            }

            input.setAttribute('disabled', 'disabled');
            button.setAttribute('disabled', 'disabled');

            self.dI.draw_update(DrawerTemplate.draw_feedback, 'sms', '');

            var params = {
                number: number
            };

            Utilities.ajax('POST', this.params['form_sms_url'], params, this, function (data) {

                input.removeAttribute('disabled');
                button.removeAttribute('disabled');

                Log.debug('Message sent correctly');

                self.dI.draw_update(DrawerTemplate.draw_feedback, 'sms', data['feedback']);


            });
        };


        // Do only one time
        if (_uploaderjs_initialized !== true) {
            Utilities.correctUrl();
            Utilities.polyfill();
        }


        return {
            start: function () {
                var scripts = document.getElementsByTagName('script');
                var position = scripts[scripts.length - 1];
                var queryString = position.src.replace(/^[^\?]+\??/, '');
                var params = Utilities.parseQuery(queryString);
                // ####
                new Drawer(position, params);

            }
        };

    }());

}

window.UploaderJS.start();



