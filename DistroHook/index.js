const express = require("express");
const axios = require("axios");

const app = express();
const PORT = 3333;

app.use(express.urlencoded({ extended:false }))
app.use(express.json());

app.post("/", async (req, res) => {

    const kwargs = {
        "sid": req.body.SmsMessageSid,
        "to": req.body.To,
        "from": req.body.From,
        "body": req.body.Body,
    }

    try {
        await axios.post("http://localhost:8000/Messenger/incoming/", kwargs);
        console.log("successful.")
        res.status(200).send("Success! Json reconstructed and sent!");
    } catch(error) {
        console.log(`unsuccessful. ${error}`);
        res.status(500).send("Failed: something went wrong with the program.");
    }
});

app.listen(PORT, () => console.log(`Listening on port ${PORT}`));