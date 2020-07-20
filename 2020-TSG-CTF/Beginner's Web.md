# Beginner's Web [168pts]

## Description

```
Why people tend to think things more difficult than it is?

http://35.221.81.216:59101/

Hint for beginners: First of all, open the link above, play it, and read through the attached source code. ...You can see the weird variable named "flag," right? Now what to do is clear: hack this web application and make it output the flag, okay? Then, it's your turn.

なぜ人々は物事を難しく考えすぎるんでしょうね?

http://35.221.81.216:59101/

初心者向けヒント: とりあえず、上のリンクを開いてみてください。適当にいじってください。で、添付したソースコードを読んでください。⋯⋯flagとかいう怪しい変数があるのが見えますね? やることは簡単、このWebアプリケーションをハックしてflagを吐き出させるだけです。では、やってみましょう。
```

## Content

In this challenge, we can send two variables via `POST`.
The first variable named `converter` indicates what converter to use (basically, `base64` and `scrypt` are provided value in options), and second the second variable named `input` indicates what content to convert using converter.
![main page](https://github.com/sumango3/ctf/blob/master/2020-TSG-CTF/Images/Beginner's_Web_main.PNG)

app.js
```JavaScript
const fastify = require('fastify');
const nunjucks = require('nunjucks');
const crypto = require('crypto');


const converters = {};

const flagConverter = (input, callback) => {
  const flag = '*** CENSORED ***';
  callback(null, flag);
};

const base64Converter = (input, callback) => {
  try {
    const result = Buffer.from(input).toString('base64');
    callback(null, result)
  } catch (error) {
    callback(error);
  }
};

const scryptConverter = (input, callback) => {
  crypto.scrypt(input, 'I like sugar', 64, (error, key) => {
    if (error) {
      callback(error);
    } else {
      callback(null, key.toString('hex'));
    }
  });
};


const app = fastify();
app.register(require('point-of-view'), {engine: {nunjucks}});
app.register(require('fastify-formbody'));
app.register(require('fastify-cookie'));
app.register(require('fastify-session'), {secret: Math.random().toString(2), cookie: {secure: false}});

app.get('/', async (request, reply) => {
  reply.view('index.html', {sessionId: request.session.sessionId});
});

app.post('/', async (request, reply) => {
  if (request.body.converter.match(/[FLAG]/)) {
    throw new Error("Don't be evil :)");
  }

  if (request.body.input.length < 20) {
    throw new Error('Too short :(');
  }

  if (request.body.input.length > 1000) {
    throw new Error('Too long :(');
  }

  converters['base64'] = base64Converter;
  converters['scrypt'] = scryptConverter;
  converters[`FLAG_${request.session.sessionId}`] = flagConverter;

  const result = await new Promise((resolve, reject) => {
    converters[request.body.converter](request.body.input, (error, result) => {
      if (error) {
        reject(error);
      } else {
        resolve(result);
      }
    });
  });

  reply.view('index.html', {
    input: request.body.input,
    result,
    sessionId: request.session.sessionId,
  });
});

app.setErrorHandler((error, request, reply) => {
  reply.view('index.html', {error, sessionId: request.session.sessionId});
});

app.listen(59101, '0.0.0.0');
```

As you see, the app first finds a function by finding matching `converter` variable as key in a `converters` dictionary.
Then, makes a Promise that only resolves if the function calls a second argument given(which is a function) with two arguments, and the first argument is null.
If not, it rejects with the first argument.
flagconverter is saved as `FLAG_${request.session.sessionId}`, but `converter` should not contain `F`, `L`, `A`, and `G`.

## Solution

### JS object prototype functions

Javascript object has many properties as default.
You may check [Mozilla document](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object) for more information.
The point is that we can use some functions that objects have as default, such as `__defineGetter__`, `__defineSetter__`

### First request

We can set `converter` as `__defineSetter__`, and `input` as `FLAG_${request.session.sessionId}`.
Then, at app's result calculating part, 
```JavaScript
const result = await new Promise((resolve, reject) => {
  converters[request.body.converter](request.body.input, (error, result) => {
    if (error) {
      reject(error);
    } else {
      resolve(result);
    }
  });
});
```
becomes
```JavaScript
const result = await new Promise((resolve, reject) => {
  converters.__defineSetter__(`FLAG_${request.session.sessionId}`, (error, result) => {
    if (error) {
      reject(error);
    } else {
      resolve(result);
    }
  });
});
```
In result, if we try to set ``converters[`FLAG_${request.session.sessionId}`]``, rather than setting value of it,
```JavaScript
(error, result) => {
  if (error) {
    reject(error);
  } else {
    resolve(result);
  }
}
```
will be executed. As setter function can only receive one argument, `reject` will be called with first argument, as long as it is not null.

### Second request

If we send any request via POST beore the first request timeout, the second request reaches following line:
```JavaScript
converters[`FLAG_${request.session.sessionId}`] = flagConverter;
```
this makes `reject(flagConverter)` to be called while generating response for the first request, and the `error` (which is `flagConverter`) is displayed in the result page.
```JavaScript
app.setErrorHandler((error, request, reply) => {
  reply.view('index.html', {error, sessionId: request.session.sessionId});
});
```
![response of the first request](https://github.com/sumango3/ctf/blob/master/2020-TSG-CTF/Images/Beginner's_Web_flag.PNG)

## Flag

    TSGCTF{Goo00o0o000o000ood_job!_you_are_rEADy_7o_do_m0re_Web}