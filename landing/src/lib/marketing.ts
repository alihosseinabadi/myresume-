/** Marketing copy: social proof, pricing and FAQ (mirrors makemycv.com). */

export const TRUSTPILOT = {
  rating: 'Excellent',
  score: '4.6',
  reviews: '3,000+ reviews',
}

export const TESTIMONIALS = [
  {
    body: 'Really good for making CV. Easy and looks awesome. Got the Job in two days. Maybe I was lucky. Maybe my CV was that good. Thanks.',
    author: 'Ivan',
    role: 'Verified review',
  },
  {
    body: 'The format was extremely easy to follow and organised. The AI suggestions were very helpful in guiding your content.',
    author: 'Ally Fox',
    role: 'Verified review',
  },
  {
    body: 'Very easy to use, the best way to complete your key to search your way for the profession of your life.',
    author: 'Rocco Giordano',
    role: 'Verified review',
  },
  {
    body: 'Easy and fast way to write an excellent CV, clear to the readers and with all the needed information.',
    author: 'Lorenzo',
    role: 'Verified review',
  },
  {
    body: 'The creation of a CV is very simple, fast and helpful. More job offers have come thanks to my new CV.',
    author: 'Milan Kulvelis',
    role: 'Verified review',
  },
]

export const HIRED_BY = [
  'Google',
  'Amazon',
  'Spotify',
  'Netflix',
  'Airbnb',
  'Uber',
  'Deloitte',
  'Siemens',
]

export type Plan = {
  id: string
  name: string
  price: string
  period: string
  note: string
  cta: string
  highlight: boolean
  badge?: string
  features: string[]
}

export const PRICING: Plan[] = [
  {
    id: 'trial',
    name: '7-day full access',
    price: '€2.90',
    period: '7 days',
    note: 'After 7 days, auto-renews for €27.95 every 4 weeks. Cancel anytime.',
    cta: 'Create my CV',
    highlight: true,
    badge: 'The most popular',
    features: [
      'CV & Cover letter builder',
      'Unlimited edits & downloads',
      'Resignation letter builder',
      'Resume checker',
      'Priority support',
    ],
  },
  {
    id: 'annual',
    name: 'Annual access',
    price: '€7.90',
    period: '/month',
    note: 'Auto-renews at €94.80 every year. Cancel anytime.',
    cta: 'Create my CV',
    highlight: false,
    features: [
      'CV & Cover letter builder',
      'Unlimited edits & downloads',
      'Resignation letter builder',
      'Resume checker',
      'Priority support',
    ],
  },
  {
    id: 'addon',
    name: 'Headshot pro',
    price: '€29.90',
    period: 'add-on',
    note: 'Satisfaction guaranteed or your money back for 30 days.',
    cta: 'Create my headshots',
    highlight: false,
    badge: 'Add-On',
    features: [
      '30 headshots',
      'Premium resolution',
      '1 hour turn-around time',
      '3 unique backdrops & outfits',
    ],
  },
]

export const FAQS = [
  {
    q: 'What is the best CV designer software?',
    a: 'To create your professional CV, using an online CV creation software is the fastest and simplest way. The templates offered are validated by recruiters, so you maximise your chances of securing an interview for the desired position. Choose the design that suits you, complete each section, then download it.',
  },
  {
    q: 'How do I create a CV with MyResume?',
    a: 'Pick a template, fill in your contact details, professional experience, training and optional sections such as interests or foreign languages. Once your CV is complete you can change the template or revise its design by customising the colours, then download it as PDF or Word.',
  },
  {
    q: 'How to create a CV without software?',
    a: 'Our online CV creator does not require tedious registration or software installation on your PC. Everything happens online, from creating your CV to downloading it. We send you a magic link to validate your account, which saves you from filling in dozens of fields before you start.',
  },
  {
    q: 'How to create a CV in PDF format?',
    a: 'All CVs you create on MyResume are exportable in PDF format. That ensures the formatting is preserved and stays readable by ATS software. Never import a CV as an image, because ATS software cannot scan it. Click “Download” and choose PDF.',
  },
  {
    q: 'How to create a CV using my phone?',
    a: 'MyResume is mobile friendly and lets you create a CV from your smartphone without downloading an app, so you can apply to a job offer the moment you find it.',
  },
  {
    q: 'Will my CV pass ATS screening?',
    a: 'Every template uses a machine-readable, single-column structure with standard section headings. The Resume checker then scores your CV against the job description and lists the exact keywords you are missing before you apply.',
  },
]

export const COVER_LETTER_POINTS = [
  'Four paragraphs: role, proof, why this company, confident close',
  'Mirrors the keywords from the job advert automatically',
  'Editable in the same editor, exported as PDF or Word',
  'Saved to your account next to the CV it belongs to',
]
