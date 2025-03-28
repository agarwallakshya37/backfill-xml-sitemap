document.getElementById("fetchSitemap").addEventListener("click", async function() {
    const sitemapUrl = document.getElementById("sitemapUrl").value.trim();
    const startDate = document.getElementById("startDate").value;
    const endDate = document.getElementById("endDate").value;
    const contentFilter = document.getElementById("contentFilter").value.trim();

    if (!sitemapUrl) {
        alert("Please enter a sitemap URL.");
        return;
    }

    try {
        const response = await fetch("http://127.0.0.1:8000/fetch_sitemap", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ sitemap_url: sitemapUrl, start_date: startDate, end_date: endDate, content_filter: contentFilter })
        });

        const data = await response.json();
        document.getElementById("output").textContent = JSON.stringify(data, null, 2);
    } catch (error) {
        console.error("Error fetching sitemap:", error);
    }
});
