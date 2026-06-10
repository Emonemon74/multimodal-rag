async function uploadPDF() {
  const fileInput = document.getElementById("pdfFile");

  if (!fileInput.files[0]) {
    alert("Please select a PDF");

    return;
  }

  const formData = new FormData();

  formData.append("file", fileInput.files[0]);

  const response = await fetch("/parse-pdf", {
    method: "POST",
    body: formData,
  });

  const data = await response.json();

  loadUploadedFiles();

  alert(data.message);
}

async function askQuestion() {
  const questionInput = document.getElementById("question");

  const question = questionInput.value;

  if (!question) {
    return;
  }

  const chatContainer = document.getElementById("chatContainer");

  chatContainer.innerHTML += `
        <div class="message user">
            ${question}
        </div>
    `;

  const botMessage = document.createElement("div");

  botMessage.className = "message bot";

  botMessage.innerHTML = "Thinking...";

  chatContainer.appendChild(botMessage);

  const response = await fetch("/ask", {
    method: "POST",

    headers: {
      "Content-Type": "application/json",
    },

    body: JSON.stringify({
      question: question,
    }),
  });

  const data = await response.json();

  let sourcesHTML = "";

  if (data.sources) {
    sourcesHTML = `
            <div class="sources">

                <strong>
                    Sources Used:
                </strong>

                <ul>

                    ${data.sources
                      .map(
                        (source) => `
                            <li>
                               <strong>
    📄 ${source.source}
</strong>
<br>
<small>
    Page: ${source.page}
</small>
                            </li>
                        `,
                      )
                      .join("")}

                </ul>

            </div>
        `;
  }

  botMessage.innerHTML = marked.parse(data.answer) + sourcesHTML;

  questionInput.value = "";

  chatContainer.scrollTop = chatContainer.scrollHeight;
}

async function loadUploadedFiles() {
  const response = await fetch("/uploaded-files");

  const data = await response.json();

  const pdfList = document.getElementById("pdfList");

  pdfList.innerHTML = "";

  data.files.forEach((file) => {
    pdfList.innerHTML += `
        <li>
            📄 ${file.filename}
            <br>
            <small>
    Pages: ${file.pages}
    <br>
    Chunks: ${file.documents}
</small>
        </li>
    `;
  });
}

loadUploadedFiles();

async function clearChat() {
  await fetch("/chat-history", {
    method: "DELETE",
  });

  document.getElementById("chatContainer").innerHTML = "";
}
