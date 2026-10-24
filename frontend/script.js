/**
 * Minimal & Modern Lovable Chatbot UI Engine
 */

document.addEventListener('DOMContentLoaded', () => {
  const appContainer = document.querySelector('.app-container');
  const promptInput = document.getElementById('promptInput');
  const sendBtn = document.getElementById('sendBtn');
  const micBtn = document.getElementById('micBtn');
  const attachBtn = document.getElementById('attachBtn');
  const fileInput = document.getElementById('fileInput');
  const fileTag = document.getElementById('fileTag');
  const modeBtn = document.getElementById('modeBtn');
  const modeMenu = document.getElementById('modeMenu');
  const selectedModeSpan = document.getElementById('selectedMode');
  const chatContainer = document.getElementById('chatContainer');
  const newChatBtn = document.getElementById('newChatBtn');
  const backendStatus = document.getElementById('backendStatus');

  let currentMode = 'Build';
  let isListening = false;
  let recognition = null;
  let attachedFile = null;

  // Auto-resize textarea
  promptInput.addEventListener('input', () => {
    promptInput.style.height = 'auto';
    promptInput.style.height = Math.min(promptInput.scrollHeight, 180) + 'px';
    
    // Toggle active state of send button
    if (promptInput.value.trim().length > 0) {
      sendBtn.classList.add('active');
    } else {
      sendBtn.classList.remove('active');
    }
  });

  // Handle Enter to send, Shift+Enter for newline
  promptInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (promptInput.value.trim().length > 0) {
        handleSendMessage();
      }
    }
  });

  sendBtn.addEventListener('click', () => {
    if (promptInput.value.trim().length > 0) {
      handleSendMessage();
    }
  });

  // Mode Dropdown Toggle
  modeBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    modeMenu.classList.toggle('show');
  });

  document.addEventListener('click', () => {
    modeMenu.classList.remove('show');
  });

  document.querySelectorAll('.dropdown-item').forEach(item => {
    item.addEventListener('click', (e) => {
      document.querySelectorAll('.dropdown-item').forEach(el => el.classList.remove('active'));
      item.classList.add('active');
      currentMode = item.getAttribute('data-mode');
      selectedModeSpan.textContent = item.textContent.trim();
      modeMenu.classList.remove('show');
    });
  });

  // File Attachment
  attachBtn.addEventListener('click', () => fileInput.click());

  fileInput.addEventListener('change', (e) => {
    if (e.target.files && e.target.files[0]) {
      attachedFile = e.target.files[0];
      fileTag.textContent = attachedFile.name;
      fileTag.style.display = 'inline-block';
      fileTag.title = attachedFile.name;
    }
  });

  // Voice Input (Web Speech API)
  if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      promptInput.value += (promptInput.value ? ' ' : '') + transcript;
      promptInput.dispatchEvent(new Event('input'));
      stopListening();
    };

    recognition.onerror = () => stopListening();
    recognition.onend = () => stopListening();

    micBtn.addEventListener('click', () => {
      if (!isListening) {
        startListening();
      } else {
        stopListening();
      }
    });
  } else {
    micBtn.addEventListener('click', () => {
      alert('Speech recognition is not supported in this browser.');
    });
  }

  function startListening() {
    try {
      recognition.start();
      isListening = true;
      micBtn.classList.add('listening');
      promptInput.setAttribute('placeholder', 'Listening...');
    } catch (e) {
      stopListening();
    }
  }

  function stopListening() {
    isListening = false;
    micBtn.classList.remove('listening');
    promptInput.setAttribute('placeholder', 'Ask Lovable to create a dashboard to...');
  }

  // Handle Message Submission
  async function handleSendMessage() {
    const userText = promptInput.value.trim();
    if (!userText) return;

    // Transition to chat view
    appContainer.classList.add('chat-active');

    // Append User Message
    appendMessage('user', userText);

    // Reset input
    promptInput.value = '';
    promptInput.style.height = 'auto';
    sendBtn.classList.remove('active');
    
    // Clear file if attached
    let attachmentName = '';
    if (attachedFile) {
      attachmentName = ` [Attached: ${attachedFile.name}]`;
      attachedFile = null;
      fileInput.value = '';
      fileTag.style.display = 'none';
    }

    // Append Typing Indicator
    const typingBubble = appendTypingIndicator();

    // Determine API URLs (local port 8000 for local development, relative '/api' on Vercel)
    const isLocalDev = window.location.protocol === 'file:' || 
                       window.location.hostname === 'localhost' || 
                       window.location.hostname === '127.0.0.1';
    const API_CHAT_URL = isLocalDev && window.location.port !== '8000' 
      ? 'http://127.0.0.1:8000/api/chat' 
      : '/api/chat';

    try {
      // Send message to FastAPI server
      const response = await fetch(API_CHAT_URL, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json' 
        },
        body: JSON.stringify({ 
          message: userText + attachmentName
        })
      });
      if (!response.ok) {
        const errJson = await response.json().catch(() => ({}));
        throw new Error(errJson.detail || `Server error: ${response.status}`);
      }
      const data = await response.json();
      removeTypingIndicator(typingBubble);
      appendMessage('ai', data.response);
    } catch (err) {
      // Graceful intelligent fallback if server isn't running
      setTimeout(() => {
        removeTypingIndicator(typingBubble);
        const fallbackReply = generateFallbackResponse(userText, currentMode);
        appendMessage('ai', fallbackReply);
      }, 700);
    }
  }

  // Append Message to UI
  function appendMessage(sender, text) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message-bubble', sender === 'user' ? 'message-user' : 'message-ai');

    if (sender === 'user') {
      msgDiv.textContent = text;
    } else {
      msgDiv.innerHTML = formatMarkdown(text);
    }

    chatContainer.appendChild(msgDiv);
    scrollToBottom(true);
    return msgDiv;
  }

  // Smooth Scroll Helper
  function scrollToBottom(smooth = true) {
    requestAnimationFrame(() => {
      const scrollHeight = Math.max(
        document.documentElement.scrollHeight,
        document.body.scrollHeight
      );
      window.scrollTo({
        top: scrollHeight,
        behavior: smooth ? 'smooth' : 'auto'
      });
    });
  }

  // Typing Indicator
  function appendTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.classList.add('message-bubble', 'message-ai');
    typingDiv.innerHTML = '<div class="typing-dots"><span></span><span></span><span></span></div>';
    chatContainer.appendChild(typingDiv);
    scrollToBottom(true);
    return typingDiv;
  }

  function removeTypingIndicator(element) {
    if (element && element.parentNode) {
      element.parentNode.removeChild(element);
    }
  }

  // Simple Markdown Formatter
  function formatMarkdown(text) {
    let html = text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');

    // Code blocks ```code```
    html = html.replace(/```([a-z]*)\n([\s\S]*?)```/g, (match, lang, code) => {
      return `<pre><code>${code.trim()}</code></pre>`;
    });

    // Inline code `code`
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

    // Bold **text**
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');

    // Paragraphs
    html = html.split('\n\n').map(p => `<p>${p.replace(/\n/g, '<br>')}</p>`).join('');

    return html;
  }

  // Fallback response for offline or direct HTML opening
  function generateFallbackResponse(query, mode) {
    const q = query.toLowerCase();
    if (mode === 'Build') {
      return `### 🚀 Building Your Request\n\nI analyzed your prompt: **"${query}"**.\n\nHere is what I'm generating for you:\n1. **Component Layout**: Structured with responsive modern flexbox/grid.\n2. **Color Palette**: Seamless aesthetic gradients & clean typography.\n3. **State Management**: Reactive data binding & minimal footprint.\n\n\`\`\`javascript\n// Quick component stub\nexport default function Dashboard() {\n  return <div className="p-6">Dashboard initialized</div>;\n}\n\`\`\`\n\nConnect **server.py** with your Gemini API key to stream real-time LLM generations!`;
    } else if (mode === 'Code') {
      return `Here is the clean code implementation for **"${query}"**:\n\n\`\`\`python\ndef process_request(data):\n    # Process your prompt\n    return {"status": "success", "result": "${query}"}\n\`\`\`\n\nLet me know if you would like me to adjust any logic or add unit tests!`;
    } else {
      return `I received your message: **"${query}"** in **${mode}** mode.\n\nTo power this with full Gemini AI reasoning, simply run \`python server.py\` in your terminal!`;
    }
  }

  // Reset New Chat with smooth reverse glide animation
  newChatBtn.addEventListener('click', () => {
    // 1. Smoothly fade out old messages
    chatContainer.style.transition = 'opacity 0.28s ease, transform 0.28s ease';
    chatContainer.style.opacity = '0';
    chatContainer.style.transform = 'translateY(10px)';

    // 2. Remove chat-active to trigger prompt box gliding back to center
    appContainer.classList.remove('chat-active');

    // 3. Reset input and scroll smoothly to top
    promptInput.value = '';
    promptInput.style.height = 'auto';
    sendBtn.classList.remove('active');
    window.scrollTo({ top: 0, behavior: 'smooth' });

    // 4. Clear messages after fade-out completes
    setTimeout(() => {
      chatContainer.innerHTML = '';
      chatContainer.style.transition = '';
      chatContainer.style.opacity = '';
      chatContainer.style.transform = '';
    }, 300);
  });

  // Check Backend Status
  const isLocalDev = window.location.protocol === 'file:' || 
                     window.location.hostname === 'localhost' || 
                     window.location.hostname === '127.0.0.1';
  const API_HEALTH_URL = isLocalDev && window.location.port !== '8000'
    ? 'http://127.0.0.1:8000/api/health'
    : '/api/health';

  fetch(API_HEALTH_URL)
    .then(res => res.json())
    .then(data => {
      if (data.status === 'ok') {
        backendStatus.textContent = 'AI Connected (' + data.model + ')';
      }
    })
    .catch(() => {
      backendStatus.textContent = 'Interactive Mode';
    });
});

