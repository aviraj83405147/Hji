const express = require('express');
const { default: makeWASocket, useSingleFileAuthState } = require('@whiskeysockets/baileys');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 5001;
app.use(cors());
app.use(express.json());

app.post('/send', async (req, res) => {
    const { message, numbers, delay, haters, creds_file } = req.body;
    const credsPath = path.join(__dirname, 'uploads', creds_file);

    if (!fs.existsSync(credsPath)) {
        return res.status(400).send("creds.json not found");
    }

    const { state, saveState } = useSingleFileAuthState(credsPath);
    const sock = makeWASocket({ auth: state });

    sock.ev.on('creds.update', saveState);

    const numList = numbers.split(',').map(n => n.trim());
    try {
        for (let number of numList) {
            const jid = number + "@s.whatsapp.net";
            await sock.sendMessage(jid, { text: message });
            console.log(`✅ Message sent to ${number}`);
            if (delay) await new Promise(r => setTimeout(r, parseInt(delay) * 1000));
        }
        res.send("✅ All messages sent successfully");
    } catch (err) {
        console.error("❌ Error:", err);
        res.status(500).send("Failed to send some messages");
    }
});

app.listen(PORT, () => {
    console.log(`🚀 Baileys backend running on http://localhost:${PORT}`);
});
