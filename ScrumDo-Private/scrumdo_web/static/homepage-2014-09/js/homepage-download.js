var head = document.getElementsByTagName("head")[0];
var fbstyle = document.createElement('link');
fbstyle.type = 'text/css';
fbstyle.rel = 'stylesheet';
fbstyle.href = 'https://90c3bdbac687e9eadd54-1d4ffd4392a4131a848fdbd6d8fe04c7.ssl.cf1.rackcdn.com/fb_digioh.css';
fbstyle.media = 'screen';
head.appendChild(fbstyle);


var jQdigioh = $;


/*! fancyBox v2.0.4 */
(function (u, q, e) {
    var l = e(u), r = e(q), a = e.fbdigioh = function () { a.open.apply(this, arguments) }, s = !1, t = null; e.extend(a, {
        version: "2.0.4", defaults: {
            padding: 15, margin: 20, width: 800, height: 600, minWidth: 200, minHeight: 200, maxWidth: 9999, maxHeight: 9999, autoSize: !0, fitToView: !0, aspectRatio: !1, topRatio: 0.5, fixed: !e.browser.msie || 6 < e.browser.version || !q.documentElement.hasOwnProperty("ontouchstart"), scrolling: "auto", wrapCSS: "fbdigioh-default", arrows: !0, closeBtn: !0, closeClick: !1, nextClick: !1, mouseWheel: !0, autoPlay: !1,
            playSpeed: 3E3, modal: !1, loop: !0, ajax: {}, keys: { next: [13, 32, 34, 39, 40], prev: [8, 33, 37, 38], close: [27] }, tpl: {
                wrap: '<div class="fbdigioh-wrap"><div class="fbdigioh-outer"><div class="fbdigioh-inner"></div></div></div>', image: '<img class="fbdigioh-image" src="{href}" alt="" />', iframe: '<iframe class="fbdigioh-iframe" name="fbdigioh-frame{rnd}" frameborder="0" hspace="0" ' + (e.browser.msie ? 'allowtransparency="true""' : "") + ' scrolling="{scrolling}" src="{href}"></iframe>', swf: '<object classid="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000" width="100%" height="100%"><param name="wmode" value="transparent" /><param name="allowfullscreen" value="true" /><param name="allowscriptaccess" value="always" /><param name="movie" value="{href}" /><embed src="{href}" type="application/x-shockwave-flash" allowfullscreen="true" allowscriptaccess="always" width="100%" height="100%" wmode="transparent"></embed></object>',
                error: '<p class="fbdigioh-error">The requested content cannot be loaded.<br/>Please try again later.</p>', closeBtn: '<div title="Close" class="fbdigioh-item fbdigioh-close"></div>', next: '<a title="Next" class="fbdigioh-item fbdigioh-next"><span></span></a>', prev: '<a title="Previous" class="fbdigioh-item fbdigioh-prev"><span></span></a>'
            }, openEffect: "fade", openSpeed: 250, openEasing: "swing", openOpacity: !0, openMethod: "zoomIn", closeEffect: "fade", closeSpeed: 250, closeEasing: "swing", closeOpacity: !0, closeMethod: "zoomOut",
            nextEffect: "elastic", nextSpeed: 300, nextEasing: "swing", nextMethod: "changeIn", prevEffect: "elastic", prevSpeed: 300, prevEasing: "swing", prevMethod: "changeOut", helpers: { overlay: { speedIn: 0, speedOut: 300, opacity: 0.8, css: { cursor: "pointer" }, closeClick: !0 }, title: { type: "float" } }
        }, group: {}, opts: {}, coming: null, current: null, isOpen: !1, isOpened: !1, wrap: null, outer: null, inner: null, player: { timer: null, isActive: !1 }, ajaxLoad: null, imgPreload: null, transitions: {}, helpers: {}, open: function (b, c) {
            e.isArray(b) || (b = [b]); if (b.length) a.close(!0),
            a.opts = e.extend(!0, {}, a.defaults, c), a.group = b, a._start(a.opts.index || 0)
        }, cancel: function () { if (!(a.coming && !1 === a.trigger("onCancel")) && (a.coming = null, a.hideLoading(), a.ajaxLoad && a.ajaxLoad.abort(), a.ajaxLoad = null, a.imgPreload)) a.imgPreload.onload = a.imgPreload.onabort = a.imgPreload.onerror = null }, close: function (b) {
            a.cancel(); if (a.current && !1 !== a.trigger("beforeClose")) a.unbindEvents(), !a.isOpen || b && !0 === b[0] ? (e(".fbdigioh-wrap").stop().trigger("onReset").remove(), a._afterZoomOut()) : (a.isOpen = a.isOpened =
            !1, e(".fbdigioh-item").remove(), a.wrap.stop(!0).removeClass("fbdigioh-opened"), a.inner.css("overflow", "hidden"), a.transitions[a.current.closeMethod]())
        }, play: function (b) {
            var c = function () { clearTimeout(a.player.timer) }, d = function () { c(); if (a.current && a.player.isActive) a.player.timer = setTimeout(a.next, a.current.playSpeed) }, g = function () { c(); e("body").unbind(".player"); a.player.isActive = !1; a.trigger("onPlayEnd") }; if (a.player.isActive || b && !1 === b[0]) g(); else if (a.current && (a.current.loop || a.current.index <
            a.group.length - 1)) a.player.isActive = !0, e("body").bind({ "afterShow.player onUpdate.player": d, "onCancel.player beforeClose.player": g, "beforeLoad.player": c }), d(), a.trigger("onPlayStart")
        }, next: function () { a.current && a.jumpto(a.current.index + 1) }, prev: function () { a.current && a.jumpto(a.current.index - 1) }, jumpto: function (b) { a.current && (b = parseInt(b, 10), 1 < a.group.length && a.current.loop && (b >= a.group.length ? b = 0 : 0 > b && (b = a.group.length - 1)), "undefined" !== typeof a.group[b] && (a.cancel(), a._start(b))) }, reposition: function (b) {
            a.isOpen &&
            a.wrap.css(a._getPosition(b))
        }, update: function () { a.isOpen && (s || (t = setInterval(function () { if (s && (s = !1, clearTimeout(t), a.current)) { if (a.current.autoSize) a.inner.height("auto"), a.current.height = a.inner.height(); a._setDimension(); a.current.canGrow && a.inner.height("auto"); a.reposition(); a.trigger("onUpdate") } }, 100)), s = !0) }, toggle: function () { if (a.isOpen) a.current.fitToView = !a.current.fitToView, a.update() }, hideLoading: function () { e("#fbdigioh-loading").remove() }, showLoading: function () { a.hideLoading(); e('<div id="fbdigioh-loading"></div>').click(a.cancel).appendTo("body") },
        getViewport: function () { return { x: l.scrollLeft(), y: l.scrollTop(), w: l.width(), h: l.height() } }, unbindEvents: function () { a.wrap && a.wrap.unbind(".fb"); r.unbind(".fb"); l.unbind(".fb") }, bindEvents: function () {
            var b = a.current, c = b.keys; b && (l.bind("resize.fb, orientationchange.fb", a.update), c && r.bind("keydown.fb", function (b) {
                var g; if (!b.ctrlKey && !b.altKey && !b.shiftKey && !b.metaKey && 0 > e.inArray(b.target.tagName.toLowerCase(), ["input", "textarea", "select", "button"])) g = b.keyCode, -1 < e.inArray(g, c.close) ? (a.close(), b.preventDefault()) :
                -1 < e.inArray(g, c.next) ? (a.next(), b.preventDefault()) : -1 < e.inArray(g, c.prev) && (a.prev(), b.preventDefault())
            }), e.fn.mousewheel && b.mouseWheel && 1 < a.group.length && a.wrap.bind("mousewheel.fb", function (b, c) { var f = e(b.target).get(0); if (0 === f.clientHeight || f.scrollHeight === f.clientHeight) b.preventDefault(), a[0 < c ? "prev" : "next"]() }))
        }, trigger: function (b) {
            var c, d = a[-1 < e.inArray(b, ["onCancel", "beforeLoad", "afterLoad"]) ? "coming" : "current"]; if (d) {
                e.isFunction(d[b]) && (c = d[b].apply(d, Array.prototype.slice.call(arguments,
                1))); if (!1 === c) return !1; d.helpers && e.each(d.helpers, function (c, f) { if (f && "undefined" !== typeof a.helpers[c] && e.isFunction(a.helpers[c][b])) a.helpers[c][b](f, d) }); e.event.trigger(b + ".fb")
            }
        }, isImage: function (a) { return a && a.match(/\.(jpg|gif|png|bmp|jpeg)(.*)?$/i) }, isSWF: function (a) { return a && a.match(/\.(swf)(.*)?$/i) }, _start: function (b) {
            var c = {}, d = a.group[b] || null, g, f, k; if ("object" === typeof d && (d.nodeType || d instanceof e)) g = !0, e.metadata && (c = e(d).metadata()); c = e.extend(!0, {}, a.opts, { index: b, element: d },
            e.isPlainObject(d) ? d : c); e.each(["href", "title", "content", "type"], function (b, f) { c[f] = a.opts[f] || g && e(d).attr(f) || c[f] || null }); if ("number" === typeof c.margin) c.margin = [c.margin, c.margin, c.margin, c.margin]; c.modal && e.extend(!0, c, { closeBtn: !1, closeClick: !1, nextClick: !1, arrows: !1, mouseWheel: !1, keys: null, helpers: { overlay: { css: { cursor: "auto" }, closeClick: !1 } } }); a.coming = c; if (!1 === a.trigger("beforeLoad")) a.coming = null; else {
                f = c.type; b = c.href; if (!f) g && (k = e(d).data("fbdigioh-type"), !k && d.className && (f = (k = d.className.match(/fbdigioh\.(\w+)/)) ?
                k[1] : null)), !f && b && (a.isImage(b) ? f = "image" : a.isSWF(b) ? f = "swf" : b.match(/^#/) && (f = "inline")), f || (f = g ? "inline" : "html"), c.type = f; "inline" === f || "html" === f ? (c.content = c.content || ("inline" === f && b ? e(b) : d), c.content.length || (f = null)) : (c.href = b || d, c.href || (f = null)); c.group = a.group; "image" === f ? a._loadImage() : "ajax" === f ? a._loadAjax() : f ? a._afterLoad() : a._error("type")
            }
        }, _error: function (b) { e.extend(a.coming, { type: "html", autoSize: !0, minHeight: "0", hasError: b, content: a.coming.tpl.error }); a._afterLoad() }, _loadImage: function () {
            a.imgPreload =
            new Image; a.imgPreload.onload = function () { this.onload = this.onerror = null; a.coming.width = this.width; a.coming.height = this.height; a._afterLoad() }; a.imgPreload.onerror = function () { this.onload = this.onerror = null; a._error("image") }; a.imgPreload.src = a.coming.href; a.imgPreload.complete || a.showLoading()
        }, _loadAjax: function () {
            a.showLoading(); a.ajaxLoad = e.ajax(e.extend({}, a.coming.ajax, {
                url: a.coming.href, error: function (b, c) { "abort" !== c ? a._error("ajax", b) : a.hideLoading() }, success: function (b, c) {
                    if ("success" === c) a.coming.content =
                    b, a._afterLoad()
                }
            }))
        }, _preload: function () { var b = a.group, c = a.current.index, d = function (b) { if (b && a.isImage(b)) (new Image).src = b }; 1 < b.length && (d(e(b[c + 1] || b[0]).attr("href")), d(e(b[c - 1] || b[b.length - 1]).attr("href"))) }, _afterLoad: function () {
            a.hideLoading(); !a.coming || !1 === a.trigger("afterLoad", a.current) ? a.coming = !1 : (a.isOpened ? (e(".fbdigioh-item").remove(), a.wrap.stop(!0).removeClass("fbdigioh-opened"), a.inner.css("overflow", "hidden"), a.transitions[a.current.prevMethod]()) : (e(".fbdigioh-wrap").stop().trigger("onReset").remove(),
            a.trigger("afterClose")), a.unbindEvents(), a.isOpen = !1, a.current = a.coming, a.coming = !1, a.wrap = e(a.current.tpl.wrap).addClass("fbdigioh-tmp " + a.current.wrapCSS).appendTo("body"), a.outer = e(".fbdigioh-outer", a.wrap).css("padding", a.current.padding + "px"), a.inner = e(".fbdigioh-inner", a.wrap), a._setContent(), a.trigger("beforeShow"), a._setDimension(), a.wrap.hide().removeClass("fbdigioh-tmp"), a.bindEvents(), a._preload(), a.transitions[a.isOpened ? a.current.nextMethod : a.current.openMethod]())
        }, _setContent: function () {
            var b,
            c, d = a.current, g = d.type; switch (g) {
                case "inline": case "ajax": case "html": b = d.content; "inline" === g && b instanceof e && (b = b.show().detach(), b.parent().hasClass("fbdigioh-inner") && b.parents(".fbdigioh-wrap").trigger("onReset").remove(), e(a.wrap).bind("onReset", function () { b.appendTo("body").hide() })); if (d.autoSize) c = e('<div class="fbdigioh-tmp"></div>').appendTo(e("body")).append(b), d.width = c.outerWidth(), d.height = c.outerHeight(!0), b = c.contents().detach(), c.remove(); break; case "image": b = d.tpl.image.replace("{href}",
                d.href); d.aspectRatio = !0; break; case "swf": b = d.tpl.swf.replace(/\{width\}/g, d.width).replace(/\{height\}/g, d.height).replace(/\{href\}/g, d.href); break; case "iframe": b = d.tpl.iframe.replace("{href}", d.href).replace("{scrolling}", d.scrolling).replace("{rnd}", (new Date).getTime())
            } if (-1 < e.inArray(g, ["image", "swf", "iframe"])) d.autoSize = !1, d.scrolling = !1; a.inner.append(b)
        }, _setDimension: function () {
            var b = a.wrap, c = a.outer, d = a.inner, g = a.current, f = a.getViewport(), k = g.margin, i = 2 * g.padding, h = g.width + i, j = g.height +
            i, l = g.width / g.height, o = g.maxWidth, m = g.maxHeight, n = g.minWidth, p = g.minHeight; f.w -= k[1] + k[3]; f.h -= k[0] + k[2]; -1 < h.toString().indexOf("%") && (h = f.w * parseFloat(h) / 100); -1 < j.toString().indexOf("%") && (j = f.h * parseFloat(j) / 100); g.fitToView && (o = Math.min(f.w, o), m = Math.min(f.h, m)); n = Math.min(h, n); p = Math.min(h, p); o = Math.max(n, o); m = Math.max(p, m); g.aspectRatio ? (h > o && (h = o, j = (h - i) / l + i), j > m && (j = m, h = (j - i) * l + i), h < n && (h = n, j = (h - i) / l + i), j < p && (j = p, h = (j - i) * l + i)) : (h = Math.max(n, Math.min(h, o)), j = Math.max(p, Math.min(j, m))); h = Math.round(h);
            j = Math.round(j); e(b.add(c).add(d)).width("auto").height("auto"); d.width(h - i).height(j - i); b.width(h); k = b.height(); if (h > o || k > m) for (; (h > o || k > m) && h > n && k > p;) j -= 10, g.aspectRatio ? (h = Math.round((j - i) * l + i), h < n && (h = n, j = (h - i) / l + i)) : h -= 10, d.width(h - i).height(j - i), b.width(h), k = b.height(); g.dim = { width: h, height: k }; g.canGrow = g.autoSize && j > p && j < m; g.canShrink = !1; g.canExpand = !1; if (h - i < g.width || j - i < g.height) g.canExpand = !0; else if ((h > f.w || k > f.h) && h > n && j > p) g.canShrink = !0; b = k - i; a.innerSpace = b - d.height(); a.outerSpace = b -
            c.height()
        }, _getPosition: function (b) { var c = a.current, d = a.getViewport(), e = c.margin, f = a.wrap.width() + e[1] + e[3], k = a.wrap.height() + e[0] + e[2], i = { position: "absolute", top: e[0] + d.y, left: e[3] + d.x }; if (c.fixed && (!b || !1 === b[0]) && k <= d.h && f <= d.w) i = { position: "fixed", top: e[0], left: e[3] }; i.top = Math.ceil(Math.max(i.top, i.top + (d.h - k) * c.topRatio)) + "px"; i.left = Math.ceil(Math.max(i.left, i.left + 0.5 * (d.w - f))) + "px"; return i }, _afterZoomIn: function () {
            var b = a.current; a.isOpen = a.isOpened = !0; a.wrap.addClass("fbdigioh-opened").css("overflow",
            "visible"); a.update(); a.inner.css("overflow", "auto" === b.scrolling ? "auto" : "yes" === b.scrolling ? "scroll" : "hidden"); if (b.closeClick || b.nextClick) a.inner.css("cursor", "pointer").bind("click.fb", b.nextClick ? a.next : a.close); b.closeBtn && e(b.tpl.closeBtn).appendTo(a.wrap).bind("click.fb", a.close); b.arrows && 1 < a.group.length && ((b.loop || 0 < b.index) && e(b.tpl.prev).appendTo(a.wrap).bind("click.fb", a.prev), (b.loop || b.index < a.group.length - 1) && e(b.tpl.next).appendTo(a.wrap).bind("click.fb", a.next)); a.trigger("afterShow");
            if (a.opts.autoPlay && !a.player.isActive) a.opts.autoPlay = !1, a.play()
        }, _afterZoomOut: function () { a.trigger("afterClose"); a.wrap.trigger("onReset").remove(); e.extend(a, { group: {}, opts: {}, current: null, isOpened: !1, isOpen: !1, wrap: null, outer: null, inner: null }) }
    }); a.transitions = {
        getOrigPosition: function () {
            var b = a.current.element, c = {}, d = 50, g = 50, f; b && b.nodeName && e(b).is(":visible") ? (f = e(b).find("img:first"), f.length ? (c = f.offset(), d = f.outerWidth(), g = f.outerHeight()) : c = e(b).offset()) : (b = a.getViewport(), c.top = b.y +
            0.5 * (b.h - g), c.left = b.x + 0.5 * (b.w - d)); return c = { top: Math.ceil(c.top) + "px", left: Math.ceil(c.left) + "px", width: Math.ceil(d) + "px", height: Math.ceil(g) + "px" }
        }, step: function (b, c) { var d, e, f; if ("width" === c.prop || "height" === c.prop) e = f = Math.ceil(b - 2 * a.current.padding), "height" === c.prop && (d = (b - c.start) / (c.end - c.start), c.start > c.end && (d = 1 - d), e -= a.innerSpace * d, f -= a.outerSpace * d), a.inner[c.prop](e), a.outer[c.prop](f) }, zoomIn: function () {
            var b = a.wrap, c = a.current, d, g; d = c.dim; if ("elastic" === c.openEffect) {
                g = e.extend({},
                d, a._getPosition(!0)); delete g.position; d = this.getOrigPosition(); if (c.openOpacity) d.opacity = 0, g.opacity = 1; b.css(d).show().animate(g, { duration: c.openSpeed, easing: c.openEasing, step: this.step, complete: a._afterZoomIn })
            } else b.css(e.extend({}, d, a._getPosition())), "fade" === c.openEffect ? b.fadeIn(c.openSpeed, a._afterZoomIn) : (b.show(), a._afterZoomIn())
        }, zoomOut: function () {
            var b = a.wrap, c = a.current, d; if ("elastic" === c.closeEffect) {
                "fixed" === b.css("position") && b.css(a._getPosition(!0)); d = this.getOrigPosition();
                if (c.closeOpacity) d.opacity = 0; b.animate(d, { duration: c.closeSpeed, easing: c.closeEasing, step: this.step, complete: a._afterZoomOut })
            } else b.fadeOut("fade" === c.closeEffect ? c.closeSpeed : 0, a._afterZoomOut)
        }, changeIn: function () {
            var b = a.wrap, c = a.current, d; "elastic" === c.nextEffect ? (d = a._getPosition(!0), d.opacity = 0, d.top = parseInt(d.top, 10) - 200 + "px", b.css(d).show().animate({ opacity: 1, top: "+=200px" }, { duration: c.nextSpeed, complete: a._afterZoomIn })) : (b.css(a._getPosition()), "fade" === c.nextEffect ? b.hide().fadeIn(c.nextSpeed,
            a._afterZoomIn) : (b.show(), a._afterZoomIn()))
        }, changeOut: function () { var b = a.wrap, c = a.current, d = function () { e(this).trigger("onReset").remove() }; b.removeClass("fbdigioh-opened"); "elastic" === c.prevEffect ? b.animate({ opacity: 0, top: "+=200px" }, { duration: c.prevSpeed, complete: d }) : b.fadeOut("fade" === c.prevEffect ? c.prevSpeed : 0, d) }
    }; a.helpers.overlay = {
        overlay: null, update: function () {
            var a, c; this.overlay.width(0).height(0); e.browser.msie ? (a = Math.max(q.documentElement.scrollWidth, q.body.scrollWidth), c = Math.max(q.documentElement.offsetWidth,
            q.body.offsetWidth), a = a < c ? l.width() : a) : a = r.width(); this.overlay.width(a).height(r.height())
        }, beforeShow: function (b) { if (!this.overlay) this.overlay = e('<div id="fbdigioh-overlay"></div>').css(b.css || { background: "black" }).appendTo("body"), this.update(), b.closeClick && this.overlay.bind("click.fb", a.close), l.bind("resize.fb", e.proxy(this.update, this)), this.overlay.fadeTo(b.speedIn || "fast", b.opacity || 1) }, onUpdate: function () { this.update() }, afterClose: function (a) {
            this.overlay && this.overlay.fadeOut(a.speedOut ||
            "fast", function () { e(this).remove() }); this.overlay = null
        }
    }; a.helpers.title = { beforeShow: function (b) { var c; if (c = a.current.title) c = e('<div class="fbdigioh-title fbdigioh-title-' + b.type + '-wrap">' + c + "</div>").appendTo("body"), "float" === b.type && (c.width(c.width()), c.wrapInner('<span class="child"></span>'), a.current.margin[2] += Math.abs(parseInt(c.css("margin-bottom"), 10))), c.appendTo("over" === b.type ? a.inner : "outside" === b.type ? a.wrap : a.outer) } }; e.fn.fbdigioh = function (b) {
        function c(b) {
            var c = [], i, h = this.rel;
            if (!b.ctrlKey && !b.altKey && !b.shiftKey && !b.metaKey) b.preventDefault(), b = e(this).data("fbdigioh-group"), "undefined" !== typeof b ? i = b ? "data-fbdigioh-group" : !1 : h && "" !== h && "nofollow" !== h && (b = h, i = "rel"), i && (c = g.length ? e(g).filter("[" + i + '="' + b + '"]') : e("[" + i + '="' + b + '"]')), c.length ? (d.index = c.index(this), a.open(c.get(), d)) : a.open(this, d)
        } var d = b || {}, g = this.selector || ""; g ? r.undelegate(g, "click.fb-start").delegate(g, "click.fb-start", c) : e(this).unbind("click.fb-start").bind("click.fb-start", c); return this
    }
})(window,
document, jQdigioh);



jQdigioh(document).ready(function () {
    var analytics_val = logSessionData();

    jQdigioh('a[href^="https://digioh.com"]').each(function () {
        var current_href = jQdigioh(this).attr('href');
        if (current_href.length > 20 && current_href.indexOf("https://digioh.com/em/") != -1) {
            if (current_href.indexOf("?") == -1) {
                jQdigioh(this).attr('href', current_href + '?lightbox=true');
            }
            else if (current_href.indexOf("lightbox=true") == -1) {
                jQdigioh(this).attr('href', current_href + '&lightbox=true');
            }
            jQdigioh(this).fbdigioh({
                type: 'iframe',
                scrolling: 'no',
                autoSize: false,
                autoHeight: true,
                width: 835,
                height: 700,
                closeClick: false,
                nextClick: false,
                openEffect: 'none',
                closeEffect: 'none'
                //afterShow: function () {
                //    jQdigioh('.fbdigioh-iframe').load(function () {
                //        jQdigioh('.fbdigioh-inner').height(jQdigioh(this).contents().find('html').height() + 30);
                //    })
                //}
            });
        }
    });
});


function create_cookie(name, value, days) {
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        var expires = "; expires=" + date.toGMTString();
    }
    else var expires = "";
    document.cookie = name + "=" + value + expires + "; path=/";
}


function read_cookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
}


function erase_cookie(name) {
    createCookie(name, "", -1);
}


function base64_encode_mod(input) {
    var output = base64_encode(input);
    output = output.split('/').join('.');
    output = output.split('+').join('-');
    output = output.split('=').join('_');
    return output;
}


function base64_decode_mod(input) {
    var output = input;
    output = output.split('.').join('/');
    output = output.split('-').join('+');
    output = output.split('_').join('=');
    output = base64_decode(output);
    return output;
}


function base64_encode(data) {
    var b64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";
    var o1, o2, o3, h1, h2, h3, h4, bits, i = 0,
        ac = 0,
        enc = "",
        tmp_arr = [];

    if (!data) {
        return data;
    }

    data = this.utf8_encode(data + '');

    do {
        o1 = data.charCodeAt(i++);
        o2 = data.charCodeAt(i++);
        o3 = data.charCodeAt(i++);

        bits = o1 << 16 | o2 << 8 | o3;

        h1 = bits >> 18 & 0x3f;
        h2 = bits >> 12 & 0x3f;
        h3 = bits >> 6 & 0x3f;
        h4 = bits & 0x3f;

        tmp_arr[ac++] = b64.charAt(h1) + b64.charAt(h2) + b64.charAt(h3) + b64.charAt(h4);
    } while (i < data.length);

    enc = tmp_arr.join('');

    var r = data.length % 3;

    return (r ? enc.slice(0, r - 3) : enc) + '==='.slice(r || 3);
}


function utf8_encode(argString) {
    if (argString === null || typeof argString === "undefined") {
        return "";
    }

    var string = (argString + ''); // .replace(/\r\n/g, "\n").replace(/\r/g, "\n");
    var utftext = "",
        start, end, stringl = 0;

    start = end = 0;
    stringl = string.length;
    for (var n = 0; n < stringl; n++) {
        var c1 = string.charCodeAt(n);
        var enc = null;

        if (c1 < 128) {
            end++;
        } else if (c1 > 127 && c1 < 2048) {
            enc = String.fromCharCode((c1 >> 6) | 192) + String.fromCharCode((c1 & 63) | 128);
        } else {
            enc = String.fromCharCode((c1 >> 12) | 224) + String.fromCharCode(((c1 >> 6) & 63) | 128) + String.fromCharCode((c1 & 63) | 128);
        }
        if (enc !== null) {
            if (end > start) {
                utftext += string.slice(start, end);
            }
            utftext += enc;
            start = end = n + 1;
        }
    }

    if (end > start) {
        utftext += string.slice(start, stringl);
    }

    return utftext;
}


function base64_decode(data) {
    var b64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";
    var o1, o2, o3, h1, h2, h3, h4, bits, i = 0,
        ac = 0,
        dec = "",
        tmp_arr = [];

    if (!data) {
        return data;
    }

    data += '';

    do {
        h1 = b64.indexOf(data.charAt(i++));
        h2 = b64.indexOf(data.charAt(i++));
        h3 = b64.indexOf(data.charAt(i++));
        h4 = b64.indexOf(data.charAt(i++));

        bits = h1 << 18 | h2 << 12 | h3 << 6 | h4;

        o1 = bits >> 16 & 0xff;
        o2 = bits >> 8 & 0xff;
        o3 = bits & 0xff;

        if (h3 == 64) {
            tmp_arr[ac++] = String.fromCharCode(o1);
        } else if (h4 == 64) {
            tmp_arr[ac++] = String.fromCharCode(o1, o2);
        } else {
            tmp_arr[ac++] = String.fromCharCode(o1, o2, o3);
        }
    } while (i < data.length);

    dec = tmp_arr.join('');
    dec = this.utf8_decode(dec);

    return dec;
}


function utf8_decode(str_data) {
    var tmp_arr = [],
        i = 0,
        ac = 0,
        c1 = 0,
        c2 = 0,
        c3 = 0;

    str_data += '';

    while (i < str_data.length) {
        c1 = str_data.charCodeAt(i);
        if (c1 < 128) {
            tmp_arr[ac++] = String.fromCharCode(c1);
            i++;
        } else if (c1 > 191 && c1 < 224) {
            c2 = str_data.charCodeAt(i + 1);
            tmp_arr[ac++] = String.fromCharCode(((c1 & 31) << 6) | (c2 & 63));
            i += 2;
        } else {
            c2 = str_data.charCodeAt(i + 1);
            c3 = str_data.charCodeAt(i + 2);
            tmp_arr[ac++] = String.fromCharCode(((c1 & 15) << 12) | ((c2 & 63) << 6) | (c3 & 63));
            i += 3;
        }
    }

    return tmp_arr.join('');
}


function logSessionData() {
    var timestamp = new Date().getTime() + "";

    var current_url = "";
    var referring_url = "";

    if (document.URL) {
        current_url = document.URL;
    }

    if (document.referrer) {
        referring_url = document.referrer;
    }

    var cookie_val = read_cookie("digioh_analytics");

    if (cookie_val != null && cookie_val.length > 0) {
        cookie_val = base64_decode_mod(cookie_val);
    }
    else {
        cookie_val = "";
    }

    cookie_val += "_digioh_data_point:";
    cookie_val += "_ddp_key:current_url" + "_ddp_val:" + current_url;
    cookie_val += "_ddp_key:referring_url" + "_ddp_val:" + referring_url;
    cookie_val += "_ddp_key:timestamp" + "_ddp_val:" + timestamp;

    cookie_val = base64_encode_mod(cookie_val);

    create_cookie("digioh_analytics", cookie_val, 365);

    return cookie_val;
}