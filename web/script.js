// Navigation Logic
const navItems = document.querySelectorAll('.nav-item');
const views = document.querySelectorAll('.view-section');
const sectionTitle = document.getElementById('section-title');
const sectionDesc = document.getElementById('section-desc');

const contentMap = {
    'parse': {
        title: "Parseur d'Expressions Logiques",
        desc: "Transformez vos chaînes de caractères en DAG (Directed Acyclic Graph) en temps réel."
    },
    'adder': {
        title: "Architecture de l'Additionneur",
        desc: "Modélisation matérielle par composition récursive de portes logiques."
    },
    'random': {
        title: "Génération Aléatoire",
        desc: "Tests de robustesse avec des circuits générés chaotiquement."
    }
};

navItems.forEach(item => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
        
        // Update Nav
        navItems.forEach(nav => nav.classList.remove('active'));
        item.classList.add('active');
        
        // Update View
        const target = item.getAttribute('data-target');
        views.forEach(view => view.classList.remove('active'));
        document.getElementById(`view-${target}`).classList.add('active');
        
        // Update Header
        sectionTitle.textContent = contentMap[target].title;
        sectionDesc.textContent = contentMap[target].desc;
        
        // Reset Graph
        document.getElementById('graph-placeholder').style.display = 'flex';
        document.getElementById('graph-target').innerHTML = '';
        
        // Hide Results
        document.querySelectorAll('.results-container').forEach(el => el.style.display = 'none');
    });
});

// Graphviz Setup
let viz = new Viz();

// App Logic
const app = {
    showLoader() {
        document.getElementById('loader').style.display = 'flex';
    },
    hideLoader() {
        document.getElementById('loader').style.display = 'none';
    },
    
    // Convert standard DOT colors to match our dark theme
    stylizeDot(dotString) {
        // Simple string replacement to force dark theme styles
        let styled = dotString;
        if(!styled.includes('bgcolor')) {
            styled = styled.replace('digraph G {', 'digraph G {\n  bgcolor="transparent";\n  node [fontname="JetBrains Mono", style="filled", fillcolor="#2a2d3e", color="#6366f1", fontcolor="#e2e8f0", penwidth="2"];\n  edge [color="#94a3b8", fontcolor="#e2e8f0"];');
        }
        return styled;
    },

    renderGraph(dotString) {
        document.getElementById('graph-placeholder').style.display = 'none';
        const finalDot = this.stylizeDot(dotString);
        
        viz.renderSVGElement(finalDot)
            .then(function(element) {
                const target = document.getElementById('graph-target');
                target.innerHTML = '';
                element.style.width = '100%';
                element.style.height = '100%';
                element.id = 'svg-graph-element';
                target.appendChild(element);
                
                // Active le zoom et le déplacement
                try {
                    svgPanZoom('#svg-graph-element', {
                        controlIconsEnabled: true,
                        zoomEnabled: true,
                        panEnabled: true,
                        fit: true,
                        center: true
                    });
                } catch(e) {}
            })
            .catch(error => {
                viz = new Viz(); // Reset instance on error
                console.error("Erreur Graphviz:", error);
                alert("Erreur lors du rendu du graphe !");
            });
    },

    async runParse() {
        this.showLoader();
        const formule = document.getElementById('formule-input').value;
        
        try {
            const res = await fetch('/api/parse', {
                method: 'POST',
                body: JSON.stringify({ formule })
            });
            const data = await res.json();
            
            if (data.success) {
                this.renderGraph(data.dot);
                
                // Build Truth table
                const tbody = document.querySelector('#truth-table tbody');
                tbody.innerHTML = '';
                
                if (data.truth_table && data.truth_table.length > 0) {
                    data.truth_table.forEach(row => {
                        const tr = document.createElement('tr');
                        tr.innerHTML = `
                            <td>[${row.inputs.join(', ')}]</td>
                            <td style="color: ${row.output === 1 ? '#10b981' : '#ef4444'}"><b>${row.output}</b></td>
                        `;
                        tbody.appendChild(tr);
                    });
                } else {
                    tbody.innerHTML = '<tr><td colspan="2">Pas de table générée (plus de 5 variables)</td></tr>';
                }
                
                document.getElementById('parse-results').style.display = 'block';
            } else {
                alert('Erreur: ' + data.error);
            }
        } catch (e) {
            console.error(e);
            alert('Erreur de connexion au serveur Python');
        }
        
        this.hideLoader();
    },

    updateAdderLabel() {
        const n = parseInt(document.getElementById('adder-n').value);
        const bitsCount = Math.pow(2, n);
        document.getElementById('adder-size-label').textContent = bitsCount + ' bits';
        
        // Update max values based on bit size
        const maxVal = Math.pow(2, bitsCount) - 1;
        document.getElementById('adder-A').max = maxVal;
        document.getElementById('adder-B').max = maxVal;
    },

    async runAdder() {
        this.showLoader();
        const n = parseInt(document.getElementById('adder-n').value);
        const bitsCount = Math.pow(2, n);
        
        // Ensure values are clamped
        const maxVal = Math.pow(2, bitsCount) - 1;
        let valA = parseInt(document.getElementById('adder-A').value) || 0;
        let valB = parseInt(document.getElementById('adder-B').value) || 0;
        valA = Math.min(Math.max(valA, 0), maxVal);
        valB = Math.min(Math.max(valB, 0), maxVal);
        document.getElementById('adder-A').value = valA;
        document.getElementById('adder-B').value = valB;
        
        const carry = parseInt(document.getElementById('adder-C').value);
        
        // Convert integer to binary array of length 'bitsCount' (little endian)
        const getBits = (val, size) => {
            const arr = [];
            let temp = val;
            for(let i=0; i<size; i++){
                arr.push(temp % 2);
                temp = Math.floor(temp / 2);
            }
            return arr;
        };
        
        const bitsA = getBits(valA, bitsCount);
        const bitsB = getBits(valB, bitsCount);
        const inputs = [...bitsA, ...bitsB, carry];
        
        try {
            const res = await fetch('/api/adder', {
                method: 'POST',
                body: JSON.stringify({ n, inputs })
            });
            const data = await res.json();
            
            if (data.success) {
                this.renderGraph(data.dot);
                
                document.getElementById('res-bin').textContent = `[${data.result.somme_binaire.join(', ')}]`;
                document.getElementById('res-dec').textContent = data.result.decimal;
                document.getElementById('res-carry').textContent = data.result.carry_out;
                
                document.getElementById('stat-nodes').textContent = data.stats.nodes;
                document.getElementById('stat-io').textContent = `${data.stats.inputs} in / ${data.stats.outputs} out`;
                
                document.getElementById('adder-results').style.display = 'block';
            } else {
                alert('Erreur: ' + data.error);
            }
        } catch (e) {
            console.error(e);
            alert('Erreur de connexion au serveur Python');
        }
        
        this.hideLoader();
    },

    async runRandom() {
        this.showLoader();
        
        try {
            const res = await fetch('/api/random', { method: 'POST' });
            const data = await res.json();
            
            if (data.success) {
                this.renderGraph(data.dot);
                document.getElementById('res-depth').textContent = data.profondeur;
                document.getElementById('random-results').style.display = 'block';
            } else {
                alert('Erreur: ' + data.error);
            }
        } catch (e) {
            console.error(e);
            alert('Erreur de connexion au serveur Python');
        }
        
        this.hideLoader();
    },

    setFormulaExample(val) {
        document.getElementById('formule-input').value = val;
    },

    insertSymbol(sym) {
        const input = document.getElementById('formule-input');
        const start = input.selectionStart;
        const end = input.selectionEnd;
        const text = input.value;
        input.value = text.substring(0, start) + sym + text.substring(end);
        input.selectionStart = input.selectionEnd = start + sym.length;
        input.focus();
    },
    
    async loadFileList() {
        const container = document.getElementById('file-list-container');
        try {
            const res = await fetch('/api/list_files', { method: 'POST' });
            // If the server returns HTML (e.g., 404 because server wasn't restarted), this will fail gracefully
            if (!res.ok) throw new Error("HTTP error " + res.status);
            
            const data = await res.json();
            if(data.success) {
                container.innerHTML = '';
                data.files.forEach(f => {
                    const div = document.createElement('div');
                    div.className = 'file-item';
                    div.textContent = f;
                    div.onclick = () => {
                        document.querySelectorAll('.file-item').forEach(el => el.classList.remove('active'));
                        div.classList.add('active');
                        app.fetchCode(f);
                    };
                    container.appendChild(div);
                });
                if(data.files.length > 0) {
                    container.firstChild.click();
                } else {
                    container.innerHTML = '<div class="placeholder-text">Aucun fichier trouvé.</div>';
                }
            } else {
                container.innerHTML = `<div class="placeholder-text" style="color:#ef4444;">Erreur serveur: ${data.error}</div>`;
            }
        } catch(e) {
            console.error(e);
            container.innerHTML = `<div class="placeholder-text" style="color:#ef4444;">Impossible de charger les fichiers. Vérifie le serveur Python.</div>`;
        }
    },

    async fetchCode(filename) {
        this.showLoader();
        
        try {
            const res = await fetch('/api/code', {
                method: 'POST',
                body: JSON.stringify({ file: filename })
            });
            const data = await res.json();
            
            if (data.success) {
                const codeTarget = document.getElementById('code-target');
                codeTarget.style.display = 'block';
                const codeEl = codeTarget.querySelector('code');
                codeEl.className = filename.endsWith('.md') ? 'language-markdown' : 'language-python';
                codeEl.textContent = data.code;
                delete codeEl.dataset.highlighted;
                hljs.highlightElement(codeEl);
            } else {
                alert('Erreur: ' + data.error);
            }
        } catch (e) {
            console.error(e);
            alert('Erreur de connexion au serveur Python');
        }
        
        this.hideLoader();
    }
};

// Update navigation logic to handle code vs graph display
navItems.forEach(item => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
        
        // Update Nav
        navItems.forEach(nav => nav.classList.remove('active'));
        item.classList.add('active');
        
        // Update View
        const target = item.getAttribute('data-target');
        views.forEach(view => view.classList.remove('active'));
        document.getElementById(`view-${target}`).classList.add('active');
        
        // Update Header
        sectionTitle.textContent = contentMap[target] ? contentMap[target].title : "Code Source Python";
        sectionDesc.textContent = contentMap[target] ? contentMap[target].desc : "Explorez le code Python original directement depuis le navigateur.";
        
        // Hide Results
        document.querySelectorAll('.results-container').forEach(el => el.style.display = 'none');
        
        if (target === 'code') {
            document.getElementById('graph-placeholder').style.display = 'none';
            document.getElementById('graph-target').style.display = 'none';
            app.loadFileList();
        } else {
            document.getElementById('code-target').style.display = 'none';
            document.getElementById('graph-target').style.display = 'block';
            document.getElementById('graph-target').innerHTML = '';
            document.getElementById('graph-placeholder').style.display = 'flex';
        }
    });
});

// Initial load effect
setTimeout(() => {
    if(document.querySelector('.nav-item.active').getAttribute('data-target') === 'parse') {
        app.runParse();
    }
}, 500);
