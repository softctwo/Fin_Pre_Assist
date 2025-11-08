import { vi, describe, it, expect, beforeEach } from 'vitest'

// Utility function tests
describe('Utility Functions', () => {
  describe('Date formatting', () => {
    it('should format date correctly', () => {
      const date = new Date('2024-01-01')
      const formatted = date.toLocaleDateString('zh-CN')
      expect(formatted).toBe('2024/1/1')
    })

    it('should handle invalid dates', () => {
      const invalidDate = new Date('invalid')
      expect(isNaN(invalidDate.getTime())).toBe(true)
    })
  })

  describe('String operations', () => {
    it('should capitalize first letter', () => {
      const capitalize = (str: string) => 
        str.charAt(0).toUpperCase() + str.slice(1)
      
      expect(capitalize('hello')).toBe('Hello')
      expect(capitalize('')).toBe('')
    })

    it('should truncate long text', () => {
      const truncate = (text: string, maxLength: number) => 
        text.length > maxLength ? text.slice(0, maxLength) + '...' : text
      
      expect(truncate('Hello World', 5)).toBe('Hello...')
      expect(truncate('Hi', 10)).toBe('Hi')
    })
  })

  describe('Array operations', () => {
    it('should filter array correctly', () => {
      const numbers = [1, 2, 3, 4, 5]
      const evenNumbers = numbers.filter(n => n % 2 === 0)
      expect(evenNumbers).toEqual([2, 4])
    })

    it('should map array correctly', () => {
      const numbers = [1, 2, 3]
      const doubled = numbers.map(n => n * 2)
      expect(doubled).toEqual([2, 4, 6])
    })

    it('should reduce array correctly', () => {
      const numbers = [1, 2, 3, 4]
      const sum = numbers.reduce((acc, n) => acc + n, 0)
      expect(sum).toBe(10)
    })
  })

  describe('Object operations', () => {
    it('should merge objects correctly', () => {
      const obj1 = { a: 1, b: 2 }
      const obj2 = { b: 3, c: 4 }
      const merged = { ...obj1, ...obj2 }
      expect(merged).toEqual({ a: 1, b: 3, c: 4 })
    })

    it('should get nested property safely', () => {
      const obj = { user: { name: 'John', age: 30 } }
      const getName = (obj: any) => obj?.user?.name ?? 'Unknown'
      
      expect(getName(obj)).toBe('John')
      expect(getName(null)).toBe('Unknown')
    })
  })
})