   // 設定碼錶按鍵：開始、暫停以及清除
            
var stopwatch = function() {
    // 開始
    var startAt = 0;
    // 每次
    var lapTime = 0;
            
    // 清除按鈕
    this.reset = function() {
        startAt = lapTime = 0;
    };
            
    // 開始按鈕
    var now = function() {
        return (new Date().getTime());
    };
            
    this.start = function() {
        startAt = startAt ? startAt : now();
    };
            
            
    // 暫停按鈕
    this.stop = function() {
        lapTime = lapTime;
        startAt = 0;
    };
            
            
    // 總共經歷的時間
    this.time = function() {
        return lapTime + (startAt ? now() - startAt : 0);
    };
            
    };
            
            
            
            
    // 設定時間的格式：時、分、秒，顯示到html
            
    var x = new stopwatch();
    var time;
    var clocktimer;
            
    // 時、分、秒、毫秒　幾位數　格式
            
    function pad(num, size) {
        var s = "00" + num;
        return s.substr(s.length - size);
    }
            
    // 時、分、秒、毫秒　時間計算
            
    function formatTime(time) {
        var h = m = s = ms = 0;
        // 停止的時間
        var newTime = ""
            
        //時
            
        h = Math.floor(time / (60 * 60 * 1000));
        time = time % (60 * 60 * 1000);
        // 分
            
        m = Math.floor(time / (60 * 1000));
        time = time % (60 * 1000);
        // 秒
        ms = time % 1000;
        s = Math.floor(time / 1000);
            
        // 顯示時間計算結果，套用到幾位數格式上
        newTime = pad(h, 2) + ":" + pad(m, 2) + ":" + pad(s, 2) + ":" + pad(ms, 3);
        return newTime;
    }
            
    // 顯示結果放到HTML檔案上
            
    function show() {
        time = document.getElementById("time");
        update();
    }
            
    function update() {
        time.innerHTML = formatTime(x.time());
    }
            
    function start() {
        clocktimer = setInterval("update()", 1);
        x.start();
    }
            
    function stop() {
        x.stop();
        clearInterval(clocktimer);
    }
            
    function reset() {
        stop();
        x.reset();
        update();
    }
            
            
            
            
            

      