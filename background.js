chrome.runtime.onInstalled.addListener(() => {
    console.log("Sitemap Parser Extension Installed");
});

// Listener for messages from popup.js
chrome.runtime.onMessage.addListener(async (message, sender, sendResponse) => {
    if (message.action === "parse_sitemap") {
        try {
            let response = await fetch("http://127.0.0.1:8000/parse_sitemap", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    sitemap_url: message.sitemap_url,
                    start_date: message.start_date,
                    end_date: message.end_date,
                    content_filter: message.content_filter
                })
            });

            let result = await response.json();
            sendResponse({ success: true, data: result });
        } catch (error) {
            console.error("Error fetching sitemap data:", error);
            sendResponse({ success: false, error: error.message });
        }
    }
});
