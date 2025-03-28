document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("fetchBtn").addEventListener("click", fetchUrls);
    document.getElementById("copyBtn").addEventListener("click", copyUrls);
});

async function fetchUrls() {
    const sitemapUrl = document.getElementById("sitemapUrl").value;
    const startDate = document.getElementById("startDate").value;
    const endDate = document.getElementById("endDate").value;
    const contentFilter = document.getElementById("contentFilter").value;

    if (!sitemapUrl || !startDate || !endDate) {
        alert("Please enter all required fields.");
        return;
    }

    try {
        const response = await fetch("/crawl", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                sitemap_url: sitemapUrl,
                start_date: startDate,
                end_date: endDate,
                content_filter: contentFilter
            })
        });

        const data = await response.json();
        if (data.error) {
            alert("Error: " + data.error);
            return;
        }

        const urlList = document.getElementById("urlList");
        urlList.innerHTML = "";

        if (data.urls) {
            Object.keys(data.urls).forEach(sitemap => {
                const heading = document.createElement("h3");
                heading.textContent = "Sitemap: " + sitemap;
                urlList.appendChild(heading);

                const urls = data.urls[sitemap];
                const list = document.createElement("ul");

                urls.forEach(url => {
                    const listItem = document.createElement("li");
                    listItem.textContent = url;
                    list.appendChild(listItem);
                });

                urlList.appendChild(list);
            });

            document.getElementById("copyBtn").style.display = "block";
        } else {
            urlList.innerHTML = "<p>No URLs found for the given criteria.</p>";
        }

    } catch (error) {
        alert("Failed to fetch data: " + error.message);
    }
}

function copyUrls() {
    const urlElements = document.querySelectorAll("#urlList li");
    const urls = Array.from(urlElements).map(li => li.textContent).join("\n");

    navigator.clipboard.writeText(urls).then(() => {
        alert("URLs copied to clipboard!");
    }).catch(err => {
        alert("Failed to copy: " + err);
    });
}
