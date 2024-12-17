document.addEventListener('DOMContentLoaded', () => {
    // Definiendo las variables pertinentes
    const addTodoForm = document.getElementById('add-todo-form');  //Formulario de registro de una nueva tarea
    const todoList = document.getElementById('todo-list');  //Elemento 'ul' para ingresar todas las tareas
    const titleInput = document.getElementById('todo-title');
    const descriptionInput = document.getElementById('todo-description');
    const titleCounter = document.getElementById('title-counter');
    const descriptionCounter = document.getElementById('description-counter');
    const inputFile = document.getElementById('inputFile');
    const getTasks = document.getElementById('getTasks');
    let todos = [];


    // Crear evento para exportar tareas
    getTasks.addEventListener("click", () => {
        exportarTareas();
    });


    // Crear evento para importar tareas
    inputFile.addEventListener("change", (e) => {
        console.log(e);
        const file = e.target.files[0];

        if (file && file.type === "application/json") {
            importarTareas(file);
            window.location.reload();  //Aplicar cambios de manera más "visual"

        } else {
            alert("Por favor, selecciona un archivo válido en formato JSON.");
            return;
        }
    });


    // Feedback en tiempo real para el título y descripción
    titleInput.addEventListener('input', () => {
        const remaining = 100 - titleInput.value.length;
        titleCounter.textContent = `${remaining} caracteres restantes`;
        titleCounter.classList.toggle("error", remaining < 0);
    });

    descriptionInput.addEventListener('input', () => {
        const remaining = 255 - descriptionInput.value.length;
        descriptionCounter.textContent = `${remaining} caracteres restantes`;
        descriptionCounter.classList.toggle("error", remaining < 0);
    });


    // Agrega un evento de escucha para manejar el envío de información
    addTodoForm.addEventListener('submit', (e) => {
        e.preventDefault();

        // Obteniendo la información necesaria
        const titulo = titleInput.value.trim();
        const descripcion = descriptionInput.value.trim();

        // Valida la longitud de las entradas de texto
        if (titulo.length === 0 || titulo.length > 100) {
            alert("El título debe tener entre 1 y 100 caracteres.");
            return;
        } else if (descripcion.length === 0 || descripcion.length > 255) {
            alert("La descripción no puede exceder los 255 caracteres.");
            return;
        }


        // Prepara la información a enviar a la DB
        const nuevaTarea = {
            titulo: titleInput.value,
            descripcion: descriptionInput.value,
            estado: true
        };

        // Establece conexión con la API para el envío de la nueva tarea
        fetch('http://127.0.0.1:8000/tareas', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(nuevaTarea)
        })
         .then(response => response.json())
         .then(data => {
            console.log("Nueva tarea creada:", data);
            todos.push(data);
            renderTodos();
            titleInput.value = '';
            descriptionInput.value = '';
         })
         .catch(error => console.error('Error:', error));
    });


    // Renderiza la interfaz al realizar alguna operación CRUD con las tareas
    function renderTodos() {
        todoList.innerHTML = '';

        todos.forEach(todo => {
            const todoItem = document.createElement('li');
            console.log(todo.estado)
            todoItem.className = `todo-item ${todo.estado ? '' : 'completed'}`;
            todoItem.innerHTML = `
                <div class="todo-header">
                    <span class="todo-title">${todo.titulo}</span>
                    <div class="todo-actions">
                        <button class="toggle-btn">${todo.estado ? 'Completar' : 'Reabrir'}</button>
                        <button class="delete-btn">Eliminar</button>
                    </div>
                </div>

                <p class="todo-description">${todo.descripcion}</p>
            `;

            const toggleBtn = todoItem.querySelector('.toggle-btn');
            const deleteBtn = todoItem.querySelector('.delete-btn');

            toggleBtn.addEventListener('click', () => toggleTodo(todo.id));
            deleteBtn.addEventListener('click', () => deleteTodo(todo.id));

            todoList.appendChild(todoItem);
        })
    }


    // Edita el estado de una tarea
    function toggleTodo(id) {
        const todo = todos.find(t => t.id === id);

        fetch(`http://127.0.0.1:8000/tareas/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                titulo: todo.titulo,
                descripcion: todo.descripcion,
                estado: !todo.estado
            })
        })
          .then(response => response.json())
          .then(data => {
            console.log(data);
            todo.estado = !todo.estado;
            renderTodos();
          })
          .catch(error => console.error('Error:', error));
    }


    // Elimina una tarea por completo
    function deleteTodo(id) {
        fetch(`http://127.0.0.1:8000/tareas/${id}`, {
            method: 'DELETE'
        })
          .then(() => {
            todos = todos.filter(t => t.id !== id);
            renderTodos();
          })
          .catch(error => console.error('Error', error))
    }


    // Ejecución inicial al momento de cargar la base de datos, para visualizar
    // las tareas guardadas en la base de datos
    function fetchTodos() {
        return fetch('http://127.0.0.1:8000/tareas')
            .then(response => {
                if(!response.ok) {
                    throw new Error('Error al obtener las tareas');
                }
                return response.json();
            })
            .then(data => {
                if(!Array.isArray(data)) {
                    throw new Error('El servidor no devolvió una lista válida de tareas');
                }

                return data.map(t => ({
                    id: t.id,
                    titulo: t.titulo,
                    descripcion: t.descripcion,
                    estado: t.estado
                }));
            });
    }

    fetchTodos()
        .then(data => {
            todos = data;
            renderTodos();
        })
    

    // Exportar tareas en formato JSON
    function exportarTareas() {
        fetch("http://127.0.0.1:8000/tareas")
            .then(response => response.json())
            .then(tareas => {
                const blob = new Blob(
                    [JSON.stringify(tareas, null, 2)], 
                    {type: "application/json"}
                );
                const url = URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = "tareas.json";
                a.click();

                URL.revokeObjectURL(url);
            })
              .catch(error => console.error("Error al exportar las tareas:", error))
    }

    // Importar tareas en formato JSON
    function  importarTareas(file) {
        const formData = new FormData();
        formData.append("file", file);

        fetch("http://127.0.0.1:8000/tareas/importar", {
            method: "POST",
            body: formData
        })
          .then(response => response.json())
          .then(data => {
                alert(data.message || "Tareas importadas correctamente.");
          })
          .catch(error => console.error("Error al importar tareas:", error));
    }
})