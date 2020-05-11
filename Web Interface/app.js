const http = require('http');
var fs = require("fs");


const hostname = '127.0.0.1';
const port = 3000;



const server = http.createServer((request, response) => {
  
    if(request.url === "/index" ||request.url === "/"){
        fs.readFile("index.html", function (err, data) {
           response.writeHead(200, {'Content-Type': 'text/html'});
           response.write(data);
           response.end();
        });
     }
     else{
        response.writeHead(200, {'Content-Type': 'text/html'});
        response.write('<b>Hey there!</b><br /><br />This is the default response. Requested URL is: ' + request.url);
        response.end();
     }
});


server.listen(port, hostname, () => {
  console.log(`Server running at http://${hostname}:${port}/`);
});