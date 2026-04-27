(function () {
  const root = document.querySelector(".pos-layout");
  if (!root) return;

  const searchInput = document.getElementById("productSearch");
  const resultsBox = document.getElementById("searchResults");
  const cartBody = document.getElementById("cartBody");
  const subtotalValue = document.getElementById("subtotalValue");
  const taxValue = document.getElementById("taxValue");
  const totalValue = document.getElementById("totalValue");
  const amountReceived = document.getElementById("amountReceived");
  const changeValue = document.getElementById("changeValue");
  const clearCart = document.getElementById("clearCart");
  const checkoutButton = document.getElementById("checkoutButton");
  const checkoutMessage = document.getElementById("checkoutMessage");
  const cashReceivedWrap = document.getElementById("cashReceivedWrap");
  const saleDialog = document.getElementById("saleDialog");
  const saleDialogFolio = document.getElementById("saleDialogFolio");
  const saleTicketLink = document.getElementById("saleTicketLink");
  const salePdfLink = document.getElementById("salePdfLink");
  const newSaleButton = document.getElementById("newSaleButton");
  const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

  const state = {
    cart: [],
    lastResults: [],
  };

  const currency = new Intl.NumberFormat("es-MX", {
    style: "currency",
    currency: "MXN",
  });

  function toNumber(value) {
    const number = Number.parseFloat(value);
    return Number.isFinite(number) ? number : 0;
  }

  function formatMoney(value) {
    return currency.format(value);
  }

  function totals() {
    return state.cart.reduce(
      (acc, item) => {
        const lineSubtotal = item.sale_price * item.quantity;
        const lineTax = lineSubtotal * item.tax_rate;
        acc.subtotal += lineSubtotal;
        acc.tax += lineTax;
        acc.total += lineSubtotal + lineTax;
        return acc;
      },
      { subtotal: 0, tax: 0, total: 0 },
    );
  }

  function renderTotals() {
    const summary = totals();
    subtotalValue.textContent = formatMoney(summary.subtotal);
    taxValue.textContent = formatMoney(summary.tax);
    totalValue.textContent = formatMoney(summary.total);
    const method = document.querySelector('input[name="paymentMethod"]:checked').value;
    if (method === "card") {
      amountReceived.value = summary.total.toFixed(2);
    }
    const change = Math.max(0, toNumber(amountReceived.value) - summary.total);
    changeValue.textContent = formatMoney(change);
  }

  function renderCart() {
    if (!state.cart.length) {
      cartBody.innerHTML = '<tr><td colspan="5" class="empty-state">Agrega productos para iniciar la venta.</td></tr>';
      renderTotals();
      return;
    }
    cartBody.innerHTML = state.cart
      .map((item) => {
        const lineTotal = (item.sale_price * item.quantity) * (1 + item.tax_rate);
        return `
          <tr data-id="${item.id}">
            <td><strong>${item.name}</strong><br><small class="muted">${item.barcode}</small></td>
            <td>
              <span class="qty-control">
                <button type="button" data-action="dec" title="Restar">-</button>
                <input type="number" min="0.01" step="0.01" value="${item.quantity}" data-action="qty">
                <button type="button" data-action="inc" title="Sumar">+</button>
              </span>
            </td>
            <td>${formatMoney(item.sale_price)}</td>
            <td>${formatMoney(lineTotal)}</td>
            <td><button class="icon-button" type="button" data-action="remove" title="Quitar">x</button></td>
          </tr>`;
      })
      .join("");
    renderTotals();
  }

  function addProduct(product) {
    const existing = state.cart.find((item) => item.id === product.id);
    if (existing) {
      if (existing.quantity + 1 > existing.stock_current) {
        showError("No hay suficiente stock para agregar mas unidades.");
        return;
      }
      existing.quantity += 1;
    } else {
      if (product.stock_current <= 0) {
        showError("Producto sin stock disponible.");
        return;
      }
      state.cart.push({
        id: product.id,
        name: product.name,
        barcode: product.barcode,
        sale_price: toNumber(product.sale_price),
        tax_rate: toNumber(product.tax_rate),
        stock_current: toNumber(product.stock_current),
        quantity: 1,
      });
    }
    searchInput.value = "";
    resultsBox.innerHTML = "";
    renderCart();
    searchInput.focus();
  }

  function showError(message) {
    checkoutMessage.hidden = false;
    checkoutMessage.className = "checkout-message error";
    checkoutMessage.textContent = message;
  }

  function clearError() {
    checkoutMessage.hidden = true;
    checkoutMessage.textContent = "";
  }

  function renderResults(products) {
    state.lastResults = products;
    if (!products.length) {
      resultsBox.innerHTML = '<p class="empty-state">Sin resultados.</p>';
      return;
    }
    resultsBox.innerHTML = products
      .map(
        (product) => `
        <button class="result-button" type="button" data-id="${product.id}">
          <span>
            <strong>${product.name}</strong>
            <small>${product.barcode} · ${product.category || "Sin categoria"} · Stock ${product.stock_current}</small>
          </span>
          <b>${formatMoney(toNumber(product.sale_price))}</b>
        </button>`,
      )
      .join("");
  }

  let searchTimer = null;
  async function searchProducts(forceExact = false) {
    const term = searchInput.value.trim();
    if (!term) {
      resultsBox.innerHTML = "";
      return;
    }
    const response = await fetch(`${root.dataset.searchUrl}?q=${encodeURIComponent(term)}`);
    const data = await response.json();
    const products = data.results || [];
    if (forceExact) {
      const exact = products.find((item) => item.barcode === term);
      if (exact) {
        addProduct(exact);
        return;
      }
      if (products.length === 1) {
        addProduct(products[0]);
        return;
      }
    }
    renderResults(products);
  }

  searchInput.addEventListener("input", () => {
    window.clearTimeout(searchTimer);
    searchTimer = window.setTimeout(() => searchProducts(false), 140);
  });

  searchInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      searchProducts(true);
    }
  });

  resultsBox.addEventListener("click", (event) => {
    const button = event.target.closest("[data-id]");
    if (!button) return;
    const product = state.lastResults.find((item) => String(item.id) === button.dataset.id);
    if (product) addProduct(product);
  });

  cartBody.addEventListener("click", (event) => {
    const action = event.target.dataset.action;
    const row = event.target.closest("tr[data-id]");
    if (!action || !row) return;
    const item = state.cart.find((entry) => String(entry.id) === row.dataset.id);
    if (!item) return;
    if (action === "inc" && item.quantity < item.stock_current) item.quantity += 1;
    if (action === "dec") item.quantity = Math.max(0.01, item.quantity - 1);
    if (action === "remove") state.cart = state.cart.filter((entry) => entry.id !== item.id);
    renderCart();
  });

  cartBody.addEventListener("change", (event) => {
    if (event.target.dataset.action !== "qty") return;
    const row = event.target.closest("tr[data-id]");
    const item = state.cart.find((entry) => String(entry.id) === row.dataset.id);
    if (!item) return;
    const requested = Math.max(0.01, toNumber(event.target.value));
    item.quantity = Math.min(requested, item.stock_current);
    renderCart();
  });

  document.querySelectorAll('input[name="paymentMethod"]').forEach((input) => {
    input.addEventListener("change", () => {
      const isCash = input.value === "cash" && input.checked;
      cashReceivedWrap.style.display = isCash ? "" : "none";
      renderTotals();
    });
  });

  amountReceived.addEventListener("input", renderTotals);

  clearCart.addEventListener("click", () => {
    state.cart = [];
    renderCart();
    searchInput.focus();
  });

  checkoutButton.addEventListener("click", async () => {
    clearError();
    if (!state.cart.length) {
      showError("El carrito esta vacio.");
      return;
    }
    checkoutButton.disabled = true;
    const method = document.querySelector('input[name="paymentMethod"]:checked').value;
    const payload = {
      payment_method: method,
      amount_received: amountReceived.value || "0",
      items: state.cart.map((item) => ({ product_id: item.id, quantity: item.quantity })),
    };
    try {
      const response = await fetch(root.dataset.checkoutUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      if (!response.ok || !data.ok) {
        throw new Error(data.error || "No se pudo registrar la venta.");
      }
      saleDialogFolio.textContent = data.folio;
      saleTicketLink.href = data.ticket_url;
      salePdfLink.href = data.pdf_url;
      saleDialog.showModal();
    } catch (error) {
      showError(error.message);
    } finally {
      checkoutButton.disabled = false;
    }
  });

  newSaleButton.addEventListener("click", () => {
    saleDialog.close();
    state.cart = [];
    amountReceived.value = "0";
    renderCart();
    searchInput.focus();
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "F2") {
      event.preventDefault();
      searchInput.focus();
    }
    if (event.key === "F4") {
      event.preventDefault();
      document.querySelector('input[name="paymentMethod"][value="cash"]').click();
      amountReceived.focus();
    }
    if (event.key === "F8") {
      event.preventDefault();
      document.querySelector('input[name="paymentMethod"][value="card"]').click();
    }
    if (event.key === "Delete" && document.activeElement !== searchInput) {
      state.cart = [];
      renderCart();
    }
  });

  renderCart();
  searchInput.focus();
})();

