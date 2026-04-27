(function () {
  const canvas = document.getElementById("salesChart");
  if (!canvas) return;

  const series = JSON.parse(canvas.dataset.series || "[]");
  const ctx = canvas.getContext("2d");
  const ratio = window.devicePixelRatio || 1;
  const cssWidth = canvas.clientWidth || 600;
  const cssHeight = Number(canvas.getAttribute("height")) || 210;
  canvas.width = cssWidth * ratio;
  canvas.height = cssHeight * ratio;
  ctx.scale(ratio, ratio);

  const padding = { top: 18, right: 16, bottom: 32, left: 48 };
  const width = cssWidth - padding.left - padding.right;
  const height = cssHeight - padding.top - padding.bottom;
  const max = Math.max(...series.map((item) => item.total), 1);
  const barGap = 10;
  const barWidth = (width - barGap * (series.length - 1)) / Math.max(series.length, 1);

  ctx.clearRect(0, 0, cssWidth, cssHeight);
  ctx.strokeStyle = "#ded8cf";
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(padding.left, padding.top);
  ctx.lineTo(padding.left, padding.top + height);
  ctx.lineTo(padding.left + width, padding.top + height);
  ctx.stroke();

  ctx.fillStyle = "#66706f";
  ctx.font = "12px Arial";
  ctx.fillText("$" + max.toFixed(0), 8, padding.top + 4);
  ctx.fillText("$0", 20, padding.top + height);

  series.forEach((item, index) => {
    const x = padding.left + index * (barWidth + barGap);
    const barHeight = (item.total / max) * height;
    const y = padding.top + height - barHeight;
    ctx.fillStyle = index % 3 === 0 ? "#0f766e" : index % 3 === 1 ? "#b7791f" : "#c24135";
    ctx.fillRect(x, y, barWidth, Math.max(2, barHeight));
    ctx.fillStyle = "#66706f";
    ctx.textAlign = "center";
    ctx.fillText(item.label, x + barWidth / 2, cssHeight - 10);
  });
})();

