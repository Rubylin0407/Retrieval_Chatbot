// for scrolling messages
function scrollToBottom() {
    var div = document.getElementById("upperid");
    div.scrollTop = div.scrollHeight;
}
scrollToBottom();

function convertToHyperlink(text) {
    // This regex looks for [title](url) pattern
    const hyperlinkRegex = /\[([^\]]+)\]\((https?:\/\/[^\)]+)\)/g;
    return text.replace(hyperlinkRegex, '<a href="$2" target="_blank">$1</a>');
}

document.getElementById("userinputform").addEventListener("submit", function (event) {
    event.preventDefault();
    formsubmitted();
});

document.getElementById('userinput').addEventListener('keydown', function(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        formsubmitted();
    }
});
if ( typeof qa_history === "undefined" && typeof system_info === "undefined" ) {
        var qa_history = [];
        var system_info="你是聊天機器人 Retrieval Bot, [檢索資料]是由 Ruby Lin 提供的。 參考[檢索資料]使用中文簡潔和專業的回覆顧客的問題, 網址使用[標題](網址)的方式提供。如果答案沒在[檢索資料]內就回答'對不起, 本次沒有檢索到相關資料, 請你換個方式詢問'\n\n";
    }
    
// sending request to python server
const formsubmitted = async () => {
    let userinput = document.getElementById('userinput').value;
    let sendbtn = document.getElementById('sendbtn');
    let userinputarea = document.getElementById('userinput');
    let upperdiv = document.getElementById('upperid');
    

    sendbtn.disabled = true;
    userinputarea.disabled = true;

    upperdiv.innerHTML = upperdiv.innerHTML + `<div class="message">
        <div class="usermessagediv">
            <div class="usermessage">
                ${userinput}
            </div>
        </div>
    </div>`;
    sendbtn.disabled = true;
    userinputarea.disabled = true;
    scrollToBottom();

    // 顯示"資料檢索中，請稍候..."
    const loadingMessage = document.createElement('div');
    loadingMessage.classList.add('message');
    loadingMessage.innerHTML = `<div class="appmessagediv">
        <div class="appmessage">
            資料檢索中，請稍候...
        </div>
    </div>`;
    upperdiv.appendChild(loadingMessage);
    scrollToBottom();

    document.getElementById('userinput').value = "";
    document.getElementById('userinput').placeholder = "Wait . . .";

    try {
        const response = await fetch("/chat", {  // Use a relative URL here
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ data: userinput, qa_history: qa_history, system_info: system_info })
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const json = await response.json();

        // Remove loading message here
        loadingMessage.remove();

        document.getElementById('userinput').placeholder = "由此輸入您的問題";

        if (json.response) {
            let message = json.message;
            
            // message = message.toString().replace(/\n/g, '<br>');
            message = convertToHyperlink(message); // Convert [title](url) to hyperlinks
            message = message.replace(/\n/g, '<br>');
            let parts = message.split('<br>');
            let index = 0;
            let partIndex = 0;
            //
            qa_history = json.qa_history ;
            system_info = json.system_info ;
            //

            upperdiv.innerHTML = upperdiv.innerHTML + `<div class="message">
                <div class="appmessagediv">
                    <div class="appmessage" id="temp"></div>
                </div>
            </div>`;

            let temp = document.getElementById('temp');

            function displayNextLetter() {
                scrollToBottom();
                if (index < parts[partIndex].length) {
                    // Check if the current character is the beginning of an anchor tag
                    if (parts[partIndex].substring(index, index + 2) === '<a') {
                        // Find the end of the anchor tag
                        let endIndex = parts[partIndex].indexOf('</a>', index) + 4;
                        if (endIndex > index + 2) {
                            // Add the whole anchor tag to the temp div
                            temp.innerHTML += parts[partIndex].substring(index, endIndex);
                            index = endIndex;
                        } else {
                            // If we can't find the end of the anchor tag, just add the current character
                            temp.innerHTML += parts[partIndex][index];
                            index++;
                        }
                    } else {
                        // If the current character is not the start of an anchor tag, add it to the temp div
                        temp.innerHTML += parts[partIndex][index];
                        index++;
                    }
                    setTimeout(displayNextLetter, 30);
                } else if (partIndex < parts.length - 1) {
                    temp.innerHTML += '<br>';
                    index = 0;
                    partIndex++;
                    setTimeout(displayNextLetter, 30);
                } else {
                    temp.removeAttribute('id');
                    sendbtn.disabled = false;
                    userinputarea.disabled = false;
                }
            }




            displayNextLetter();
            scrollToBottom();
        } else {
            let message = json.message;
            upperdiv.innerHTML = upperdiv.innerHTML +
                `<div class="message">
                    <div class="appmessagediv">
                        <div class="appmessage"  style="border: 1px solid red;">
                            ${message}
                        </div>
                    </div>
                </div>`;
            sendbtn.disabled = false;
            userinputarea.disabled = false;
        }

        scrollToBottom();
    } catch (error) {
        console.error(error);
        // Remove loading message
        loadingMessage.remove();
    }
};