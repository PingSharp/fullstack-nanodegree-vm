from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import cgi
import restaurentApi

class WebServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        restaurants = restaurentApi.getAllRestaurants()
        if self.path.endswith("/restaurants"):
           
            
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            output = ""
            output += "<html><body>"
            output += "<h1>restaurants list:</h1><ul>"
            for res in restaurants:
                output += '''
                <li>%s</li>
                <a href='/%d/edit'>edit</a>
                <a href='/%d/delete'>delete</a>
                '''%(res.name, res.id, res.id)
            
            output += "</ul> <a href='/new'>add new restaurant</a></body></html>"
            self.wfile.write(output)
            return
        elif self.path.endswith("/new"):
            stringArray = self.path.split('/');
            index = stringArray[1]
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            output = ""
            output += "<html><body>"
            output += "<h1>add new restaurant</h1>"
            output += '''<form method='POST' enctype='multipart/form-data' action='/new'>
            <h2>Please give the name for the new restaurant:</h2><input name="message" type="text" >
            <input type="submit" value="Submit the Change">
           
            '''
            output += "</body></html>"
            self.wfile.write(output)
            return
        elif self.path.endswith("/edit"):
            stringArray = self.path.split('/');
            index =int(stringArray[1])
            res = restaurentApi.getRestaurantById(index)
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            output = ""
            output += "<html><body>"
            output += "<h1>edit restaurant:%s</h1>"%res.name
            output += '''<form method='POST' enctype='multipart/form-data' action='%s/edit'>
            <h2>Please give the new name for the restaurant:</h2><input name="message" type="text" >
            <input type="submit" value="Submit the Change">
           
            '''%index
            output += "</body></html>"
            self.wfile.write(output)
            return
        elif self.path.endswith("/delete"):
            stringArray = self.path.split('/');
            index =int(stringArray[1])
            res = restaurentApi.getRestaurantById(index)
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            output = ""
            output += "<html><body>"
            output += "<h1>delete restaurant:%s</h1>"%res.name
            output += '''<form method='POST' enctype='multipart/form-data' action='%s/delete'>
            <h2>Are you sure you want to delete the restaurant?</h2>
            <input type="submit" value="Delete">
           
            '''%index
            output += "</body></html>"
            self.wfile.write(output)
            return
        else:
            self.send_error(404,'File Not Found: %s' %self.path)
    def do_POST(self):
        try:
            if self.path.endswith("/new"):

                ctype,pdict = cgi.parse_header(
                    self.headers.getheader('content-type')
                )
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile,pdict)
                    messagecontent = fields.get('message')
                    if messagecontent == "":
                        print("please add a name for your restaurant")
                    else:
                        restaurentApi.addNewRestaurant(messagecontent)
                self.send_response(301)
                self.send_header('Content-type','text/html')
                self.send_header('Location','/restaurants')
                self.end_headers()
                return
            elif self.path.endswith("/edit"):
                stringArray = self.path.split('/');
                index = int(stringArray[1])
                self.send_response(301)
                self.send_header('Content-type','text/html')
                self.end_headers()
                ctype,pdict = cgi.parse_header(
                    self.headers.getheader('content-type')
                )
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile,pdict)
                    messagecontent = fields.get('message')
                    if messagecontent == "":
                        print("please add a new name for your restaurant")
                    else:
                        restaurentApi.changeNameOfRestaurant(index,messagecontent)
                output = ""
                output += "<html><body>"
                output += " <h2> Okay, you have changed the restaurant name to : </h2>"
                output += "<h1> %s </h1>" % messagecontent[0]
                output += '''<form method='POST' enctype='multipart/form-data' action='/edit'>
                <h2>Please give the new name for the restaurant:</h2><input name="message" type="text" >
                <input type="submit" value="Submit the Change">
                </form>
                '''
                output += "</body></html>"
                self.wfile.write(output)
            elif self.path.endswith("/delete"):
                stringArray = self.path.split('/');
                index = int(stringArray[1])
                self.send_response(301)
                self.send_header('Content-type','text/html')
                self.end_headers()
                ctype,pdict = cgi.parse_header(
                    self.headers.getheader('content-type')
                )
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile,pdict)
                   
                    restaurentApi.deleteRestaurant(index)
                output = ""
                output += "<html><body>"
                output += " <h2> Okay, you have deleteded the restaurant succesfully : </h2>"
                output += '''<a href="/restaurants">Go back to restaurant lists</a>
                '''
                output += "</body></html>"
                self.wfile.write(output)
        except:
            pass

def main():
    try:
        port = 8080
        server = HTTPServer(('',port),WebServerHandler)
        print ("Web Server running on port %s"%port)
        server.serve_forever()
    except KeyboardInterrupt:
        print (" ^C entered, stopping web server....")
        server.socket.close()

if __name__ == '__main__':
    main()