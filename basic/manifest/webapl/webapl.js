// 모의 애플리케이션
//
const express = require('express')
const app = express()
var start = Date.now()

// Liveness 프로브 핸들러
// 기동 후 40초가 되면, 500 에러를 반환한다.
// 그 전까지는 HTTP 200 OK를 반환한다.
// 즉, 40초가 되면, Liveness프로브가 실패하여 컨테이너가 재기동한다. 
//
app.get('/healthz', function(request, response) {
    var msec = Date.now() - start
    var code = 200
    if (msec > 40000 ) {
	code = 500
    }
    console.log('GET /healthz ' + code)
    response.status(code).send('OK')
})

// Rediness 프로브 핸들러
// 애플리케이션의 초기화 시간으로 
// 기동 후 20초 지나고 나서부터 HTTP 200을 반환한다. 
// 그 전까지는 HTTPS 200 OK를 반환한다.
app.get('/ready', function(request, response) {
    var msec = Date.now() - start
    var code = 500
    if (msec > 20000 ) {
	code = 200
    }
    console.log('GET /ready ' + code)
    response.status(code).send('OK')
})

// 첫 화면
//
app.get('/', function(request, response) {
    console.log('GET /')
    response.send('Hello from Node.js')
})

// 서버 포트 번호
//
app.listen(3000);
