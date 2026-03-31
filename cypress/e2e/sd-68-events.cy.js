describe('Events Page', () => {

  const apiUrl = '/api/events/'

  // 🟢 SD-T1 – Events with full information
  it('SD-T1 - displays events with full information', () => {

    cy.intercept('GET', apiUrl, {
      statusCode: 200,
      body: {
        total: 2,
        events: [
          {
            event_id: 1,
            name: 'Tech Conference',
            date: '2025-05-20',
            time: '18:00',
            place: 'Vilnius',
            price: 10,
            categories: ['Tech', 'IT']
          },
          {
            event_id: 2,
            name: 'Music Night',
            date: '2025-05-21',
            time: '19:30',
            place: 'Kaunas',
            price: 5.5,
            categories: ['Music']
          }
        ]
      }
    })

    cy.visit('/events')

    cy.get('.event-item').should('have.length', 2)

    cy.get('.event-item').eq(0).within(() => {
      cy.contains('h2', 'Tech Conference')
      cy.contains(/^Date:/).parent().should('contain.text', '2025-05-20 18:00')
      cy.contains(/^Place:/).parent().should('contain.text', 'Vilnius')
      cy.contains(/^Price:/).parent().should('contain.text', '10,00 €')
      cy.contains(/^Categories:/).parent().should('contain.text', 'Tech, IT')
    })

    cy.get('.event-item').eq(1).within(() => {
      cy.contains('h2', 'Music Night')
      cy.contains(/^Date:/).parent().should('contain.text', '2025-05-21 19:30')
      cy.contains(/^Place:/).parent().should('contain.text', 'Kaunas')
      cy.contains(/^Price:/).parent().should('contain.text', '5,50 €')
      cy.contains(/^Categories:/).parent().should('contain.text', 'Music')
    })

    cy.contains('Total: 2')
  })


  // 🔴 TC2 – No name (event hidden)
  it('TC2 - hides event without name', () => {

    cy.intercept('GET', apiUrl, {
      statusCode: 200,
      body: {
        total: 1,
        events: [
          {
            event_id: 1,
            name: '',
            date: '2025-05-20',
            time: '18:00',
            place: 'Vilnius',
            price: 10,
            categories: ['Tech']
          }
        ]
      }
    })

    cy.visit('/events')

    cy.get('.event-item').should('have.length', 0)
    cy.contains('No events found. Go back to subjects.')
  })


  // 🔴 TC3 – No date (event hidden)
  it('TC3 - hides event without date', () => {

    cy.intercept('GET', apiUrl, {
      statusCode: 200,
      body: {
        total: 1,
        events: [
          {
            event_id: 1,
            name: 'Test Event',
            date: null,
            time: '18:00',
            place: 'Vilnius',
            price: 10,
            categories: ['Tech']
          }
        ]
      }
    })

    cy.visit('/events')

    cy.get('.event-item').should('have.length', 0)
  })


  // 🟡 TC4 – Missing time
  it('TC4 - shows only date when time is missing', () => {

    cy.intercept('GET', apiUrl, {
      statusCode: 200,
      body: {
        total: 1,
        events: [
          {
            event_id: 1,
            name: 'Test Event',
            date: '2025-05-20',
            time: null,
            place: 'Vilnius',
            price: 10,
            categories: ['Tech']
          }
        ]
      }
    })

    cy.visit('/events')

    cy.contains('2025-05-20')
    cy.contains('18:00').should('not.exist')
  })


  // 🟡 TC5 – Missing place
  it('TC5 - shows "-" when place is missing', () => {

    cy.intercept('GET', apiUrl, {
      statusCode: 200,
      body: {
        total: 1,
        events: [
          {
            event_id: 1,
            name: 'Test Event',
            date: '2025-05-20',
            time: '18:00',
            place: null,
            price: 10,
            categories: ['Tech']
          }
        ]
      }
    })

    cy.visit('/events')

    cy.contains('-')
  })


  // 🟡 TC6 – Missing price
  it('TC6 - shows "-" when price is missing', () => {

    cy.intercept('GET', apiUrl, {
      statusCode: 200,
      body: {
        total: 1,
        events: [
          {
            event_id: 1,
            name: 'Test Event',
            date: '2025-05-20',
            time: '18:00',
            place: 'Vilnius',
            price: null,
            categories: ['Tech']
          }
        ]
      }
    })

    cy.visit('/events')

    cy.contains('Price:')
    cy.contains('-')
  })


  // 🟡 TC7 – Zero price
  it('TC7 - shows 0,00 € when price is 0', () => {

    cy.intercept('GET', apiUrl, {
      statusCode: 200,
      body: {
        total: 1,
        events: [
          {
            event_id: 1,
            name: 'Free Event',
            date: '2025-05-20',
            time: '18:00',
            place: 'Vilnius',
            price: 0,
            categories: ['Tech']
          }
        ]
      }
    })

    cy.visit('/events')

    cy.get('.event-item').first().contains(/Price:\s*0,00\s*€/)
  })


  // 🟡 TC8 – Missing categories
  it('TC8 - shows "-" when categories are missing', () => {

    cy.intercept('GET', apiUrl, {
      statusCode: 200,
      body: {
        total: 1,
        events: [
          {
            event_id: 1,
            name: 'Test Event',
            date: '2025-05-20',
            time: '18:00',
            place: 'Vilnius',
            price: 10,
            categories: []
          }
        ]
      }
    })

    cy.visit('/events')

    cy.contains('Categories:')
    cy.contains('-')
  })


  // 🟢 TC9 – Total count
  it('TC9 - shows total events count', () => {

    cy.intercept('GET', apiUrl, {
      statusCode: 200,
      body: {
        total: 2,
        events: [
          {
            event_id: 1,
            name: 'Event 1',
            date: '2025-05-20',
            time: '18:00',
            place: 'Vilnius',
            price: 10,
            categories: ['Tech']
          },
          {
            event_id: 2,
            name: 'Event 2',
            date: '2025-05-21',
            time: '19:00',
            place: 'Kaunas',
            price: 5,
            categories: ['Music']
          }
        ]
      }
    })

    cy.visit('/events')

    cy.contains('Total: 2')
    cy.get('.event-item').should('have.length', 2)
  })


  // 🔵 TC10 – Loading state
  it('TC10 - shows loading state', () => {

    cy.intercept('GET', apiUrl, (req) => {
      req.on('response', (res) => {
        res.setDelay(1000)
      })
    })

    cy.visit('/events')

    cy.contains('Loading events...')
  })


  // 🔴 TC11 – Error state
  it('TC11 - shows error message when API fails', () => {

    cy.intercept('GET', apiUrl, {
      statusCode: 500
    })

    cy.visit('/events')

    cy.contains('Failed to load').should('exist')
  })


  // 🔴 TC12 – Empty list
  it('TC12 - shows empty state message', () => {

    cy.intercept('GET', apiUrl, {
      statusCode: 200,
      body: {
        total: 0,
        events: []
      }
    })

    cy.visit('/events')

    cy.contains('No events found. Go back to subjects.')
  })

})