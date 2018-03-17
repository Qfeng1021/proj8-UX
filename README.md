Author: Qianyi Feng

qfeng@uoregon.edu

Note:

Add the function on the previous project.

Sumbit the brevet data on 0.0.0.0:5002 first, then goto 0.0.0.0:5000/api/register to register the username 

and password. If the username exists it would jump to the error page. After register the users the page would jump to 

login. After login, the page would jump to the page with token. Add listAll, listAllCsv...after 0.0.0.0:5000/could access

 the data directly without adding token. The token is valid in 300s. Type logout after 5000 would logout user.

The php page of 5001 does not work but access from the address with 5000 and 5002 could work.

(get the token on 0.0.0.0:5000/api/token?username=test2&password=123456, then the website would jump to the token.

Copy the token without the quotation mark, put on 0.0.0.0:5000/listAll?token=[the copied token] (or replace listAll to any

 other requests), and then the results would display.)(proj7)
