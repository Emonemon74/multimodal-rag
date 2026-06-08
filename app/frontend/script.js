async function uploadPDF() {

    const fileInput =
        document.getElementById(
            "pdfFile"
        );

    if (!fileInput.files[0]) {

        alert(
            "Please select a PDF"
        );

        return;
    }

    const formData =
        new FormData();

    formData.append(
        "file",
        fileInput.files[0]
    );

    const response =
        await fetch(
            "/parse-pdf",
            {
                method: "POST",
                body: formData
            }
        );

    const data =
        await response.json();

    alert(data.message);
}


async function askQuestion() {

    const questionInput =
        document.getElementById("question");

    const question =
        questionInput.value;

    if (!question) {
        return;
    }

    const chatContainer =
        document.getElementById("chatContainer");

    // USER MESSAGE

    chatContainer.innerHTML += `
        <div class="message user">
            ${question}
        </div>
    `;

    // BOT MESSAGE

    const botMessage =
        document.createElement("div");

    botMessage.className =
        "message bot";

    botMessage.innerHTML =
        "Thinking...";

    chatContainer.appendChild(
        botMessage
    );

    chatContainer.scrollTop =
        chatContainer.scrollHeight;

    // API CALL

    const response = await fetch(
        "/ask",
        {
            method: "POST",

            headers: {
                "Content-Type":
                    "application/json"
            },

            body: JSON.stringify({
                question: question
            })
        }
    );

    const reader =
        response.body.getReader();

    const decoder =
        new TextDecoder();

    let fullText = "";

    botMessage.innerHTML = "";

    while (true) {

        const {
            done,
            value
        } = await reader.read();

        if (done) {
            break;
        }

        const chunk =
            decoder.decode(value);

        fullText += chunk;

        botMessage.innerHTML =
            marked.parse(fullText);

        chatContainer.scrollTop =
            chatContainer.scrollHeight;
    }

    questionInput.value = "";
}