import http.server
import socketserver
import json
import os
import urllib.parse
import tempfile
import webbrowser
import threading

# Import the graphython modules
from modules.open_digraph import open_digraph
from modules.bool_circ import bool_circ

PORT = 8080
DIRECTORY = "web"

class GraphythonAPIHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def get_dot_string(self, circuit):
        temp_dir = tempfile.gettempdir()
        dot_path = os.path.join(temp_dir, "temp_graph.dot")
        circuit.save_as_dot_file(dot_path, verbose=True)
        with open(dot_path, 'r') as f:
            dot_content = f.read()
        return dot_content

    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)
        
        if parsed_path.path == '/api/parse':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            formule = data.get('formule', "((x0)&(~(x1)))")
            
            try:
                circuit, variables = bool_circ.from_string(formule)
                dot = self.get_dot_string(circuit)
                
                # Dynamic truth table
                truth_table = []
                import itertools
                vars_sorted = sorted(list(variables))
                
                # Limit to 5 variables max to avoid server freeze
                if len(vars_sorted) <= 5:
                    for inputs in itertools.product([0, 1], repeat=len(vars_sorted)):
                        res = circuit.evaluate(list(inputs))
                        out_val = res[0] if (res and len(res) > 0) else "Erreur (Vide)"
                        truth_table.append({"inputs": list(inputs), "output": out_val})
                
                response = {
                    "success": True,
                    "dot": dot,
                    "variables": vars_sorted,
                    "truth_table": truth_table
                }
            except Exception as e:
                import traceback
                response = {"success": False, "error": str(e), "trace": traceback.format_exc()}
                
            self._set_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        elif parsed_path.path == '/api/adder':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            
            n = data.get('n', 1)
            try:
                adder = bool_circ.Adder(n)
                dot = self.get_dot_string(adder)
                
                entrees = data.get('inputs', [1, 1, 0, 1, 0])
                resultat = adder.evaluate(entrees)
                
                somme_binaire = resultat[:-1]
                carry = resultat[-1]
                
                val_decimale = 0
                for i, bit in enumerate(somme_binaire):
                    val_decimale += bit * (2**i)
                val_decimale += carry * (2**len(somme_binaire))
                
                stats = {
                    "nodes": len(adder.get_nodes()),
                    "inputs": len(adder.get_input_ids()),
                    "outputs": len(adder.get_output_ids())
                }
                
                response = {
                    "success": True,
                    "dot": dot,
                    "stats": stats,
                    "result": {
                        "somme_binaire": somme_binaire,
                        "carry_out": carry,
                        "decimal": val_decimale
                    }
                }
            except Exception as e:
                response = {"success": False, "error": str(e)}
                
            self._set_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        elif parsed_path.path == '/api/random':
            try:
                circuit_rand = bool_circ.random_bool_circ_with_io(n=15, bound=2, nb_inputs=3, nb_outputs=2)
                dot = self.get_dot_string(circuit_rand)
                
                prof = 0
                try:
                    prof = circuit_rand.profondeur_graphe()
                except Exception:
                    pass
                    
                response = {
                    "success": True,
                    "dot": dot,
                    "profondeur": prof
                }
            except Exception as e:
                response = {"success": False, "error": str(e)}
                
            self._set_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        elif parsed_path.path == '/api/list_files':
            try:
                base_dir = os.path.dirname(os.path.abspath(__file__))
                modules_dir = os.path.join(base_dir, 'modules')
                files_list = []
                for root, dirs, files in os.walk(modules_dir):
                    if '__pycache__' in root:
                        continue
                    for file in files:
                        if file.endswith('.py'):
                            files_list.append(file)
                files_list.sort()
                response = {"success": True, "files": files_list}
            except Exception as e:
                response = {"success": False, "error": str(e)}
            self._set_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        elif parsed_path.path == '/api/code':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            
            filename = data.get('file', 'bool_circ.py')
            # Prevent directory traversal attacks
            if '..' in filename or filename.startswith('/'):
                response = {"success": False, "error": "Accès interdit"}
            else:
                base_dir = os.path.dirname(os.path.abspath(__file__))
                modules_dir = os.path.join(base_dir, 'modules')
                filepath = os.path.normpath(os.path.join(modules_dir, filename))
                if not filepath.startswith(modules_dir):
                    response = {"success": False, "error": "Accès interdit"}
                else:
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            code = f.read()
                        response = {"success": True, "code": code}
                    except Exception as e:
                        response = {"success": False, "error": str(e)}
                
            self._set_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_error(404, "Endpoint non trouvé")

def open_browser():
    # Wait a tiny bit for the server to start
    import time
    time.sleep(1)
    webbrowser.open(f'http://localhost:{PORT}')

if __name__ == "__main__":
    if not os.path.exists(DIRECTORY):
        os.makedirs(DIRECTORY)
        
    print(f"===========================================================")
    print(f" DÉMARRAGE DU SERVEUR GRAPHYTHON DEMO ")
    print(f"===========================================================")
    print(f"Serveur local lancé sur http://localhost:{PORT}")
    print(f"Le navigateur va s'ouvrir automatiquement...")
    
    # Start browser in a thread
    threading.Thread(target=open_browser).start()
    
    # Create a custom server class to allow address reuse
    class ReusableTCPServer(socketserver.TCPServer):
        allow_reuse_address = True
        
    # Start server
    with ReusableTCPServer(("", PORT), GraphythonAPIHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nArrêt du serveur.")
            httpd.server_close()
