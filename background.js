chrome.runtime.onInstalled.addListener(() => {
    console.log("Sitemap Parser Extension Installed");
});

chrome.action.onClicked.addListener(() => {
    chrome.tabs.create({ url: "index.html" });
});