// mission-control/components/status-widget.js
document.addEventListener('DOMContentLoaded', () => {
    const statusContainer = document.getElementById('mission-status-widget');
    if (!statusContainer) return;

    // Fetch the herbs list from HerbCraft to get the count
    fetch('../herbcraft/herbs.json')
        .then(response => response.json())
        .then(data => {
            const count = Array.isArray(data) ? data.length : 0;
            statusContainer.innerHTML = `
                <div style="padding: 1rem; background: #222; border-radius: 8px; border: 1px solid #444;">
                    <h3 style="margin: 0; color: #4ade80;">HerbCraft Status</h3>
                    <p style="font-size: 2rem; margin: 0.5rem 0;">${count} <span style="font-size: 1rem; color: #888;">pages generated</span></p>
                    <div style="height: 4px; background: #333; border-radius: 2px;">
                        <div style="width: ${Math.min(count, 100)}%; height: 100%; background: #4ade80; border-radius: 2px;"></div>
                    </div>
                </div>
            `;
        })
        .catch(err => {
            console.error('Failed to load HerbCraft status:', err);
            statusContainer.innerHTML = '<p style="color: #ff5555;">Failed to load HerbCraft metrics.</p>';
        });
});