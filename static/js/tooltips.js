class Tooltip {
    constructor(element) {
      this.element = element;
      this.tooltip = element.getAttribute('data-tooltip');
      this.createTooltipElement();
    }
  
    createTooltipElement() {
      this.tooltipElement = document.createElement('div');
      this.tooltipElement.classList.add('tooltip');
      this.tooltipElement.textContent = this.tooltip;
      document.body.appendChild(this.tooltipElement);
  
      this.element.addEventListener('mouseenter', this.showTooltip.bind(this));
      this.element.addEventListener('mouseleave', this.hideTooltip.bind(this));
    }
  
    showTooltip(event) {
      const rect = this.element.getBoundingClientRect();
      this.tooltipElement.style.left = `${rect.left + rect.width / 2}px`;
      this.tooltipElement.style.top = `${rect.top - 5}px`;
      this.tooltipElement.classList.add('show');
    }
  
    hideTooltip() {
      this.tooltipElement.classList.remove('show');
    }
  }
  
  document.addEventListener('DOMContentLoaded', () => {
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(el => {
        const tooltipEl = document.createElement('div');
        tooltipEl.classList.add('tooltip');
        tooltipEl.style.position = 'absolute';
        tooltipEl.style.display = 'none';
        document.body.appendChild(tooltipEl);

        el.addEventListener('mouseenter', (event) => {
            const tooltip = el.getAttribute('data-tooltip');
            tooltipEl.textContent = tooltip;
            tooltipEl.style.display = 'block';
            const rect = el.getBoundingClientRect();
            tooltipEl.style.left = `${rect.left + window.scrollX + rect.width / 2}px`;
            tooltipEl.style.top = `${rect.top + window.scrollY - tooltipEl.offsetHeight - 5}px`;
        });

        el.addEventListener('mouseleave', () => {
            tooltipEl.style.display = 'none';
        });
    });
});