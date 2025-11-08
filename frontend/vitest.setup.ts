import '@testing-library/jest-dom'

// Mock window.matchMedia for Ant Design responsive components
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => {},
  }),
})

// Mock window.getComputedStyle to fix jsdom issue
Object.defineProperty(window, 'getComputedStyle', {
  writable: true,
  value: (elt: Element) => {
    return {
      getPropertyValue: (prop: string) => {
        return '';
      }
    };
  }
});