/**
 * 30-Day Content Calendar for AIGIS Operator Field Notes Series
 * Week 1: Foundation + Authority
 * Week 2: Education + Playbooks
 * Week 3: Credibility Amplification + Fellowship Launch
 * Week 4: Scale and Signal Optimization
 */

export const contentCalendar = [
  // === WEEK 1: Foundation + Authority ===
  {
    day: 1,
    week: 1,
    format: "Text + Image",
    headline: "We ran 18 operator interviews this month. Here's the single thing every healthy business is missing.",
    content: {
      observation: "Every high-performing clinic we spoke to had one thing in common: they track lead conversion at the operator level, not just the clinic level.",
      examples: [
        "A 3-location practice discovered their top operator converts 2.3x better than their lowest—now they route leads accordingly.",
        "Another clinic found that follow-up timing (not just frequency) was the differentiator—their best operator responds within 4 minutes."
      ]
    },
    cta: "Comment 'Notes' and I'll DM the short checklist.",
    repurpose: "Thread on X summarizing 3 excerpts.",
    isVideo: false
  },
  {
    day: 2,
    week: 1,
    format: "45s Native Video (founder)",
    headline: "If you run a multi-location clinic, listen.",
    content: {
      hook: "Walk into office / soft B-roll, opener: 'If you run a multi-location clinic, listen.'",
      script: "One micro-insight: The clinics seeing 30%+ growth aren't spending more on ads. They're measuring operator-level conversion. One metric changed everything for a 5-location practice we worked with.",
      duration: "30-45 seconds"
    },
    cta: "Say '60-day pilot' if you want the framework.",
    repurpose: "Short 10s cut as ad.",
    isVideo: true,
    videoNote: "⚠️ VIDEO: This content requires hand-generated video. Record founder walking into office with soft B-roll."
  },
  {
    day: 3,
    week: 1,
    format: "Carousel (5 slides)",
    headline: "How we define a convertible lead for AI execution (5 questions)",
    content: {
      slides: [
        { question: "What's the immediate pain point?", explanation: "If they can't articulate a specific problem happening right now, they're not ready to convert. We look for urgency indicators like 'we're losing revenue' or 'our team is overwhelmed.'" },
        { question: "Do they have budget allocated?", explanation: "Even if they're interested, without budget or approval authority, they're just researching. We ask: 'Is this something you'd invest in this quarter?'" },
        { question: "What happens if they don't solve this?", explanation: "The cost of inaction matters. If they can't articulate consequences—lost revenue, team burnout, competitive disadvantage—they're not feeling enough pain to convert." },
        { question: "What's their decision timeline?", explanation: "A lead who says 'maybe next year' isn't convertible. We qualify leads who can make decisions within 60-90 days." },
        { question: "Have they tried a solution before?", explanation: "Leads who've attempted to solve this problem (and failed) are more likely to convert. They understand the complexity." }
      ]
    },
    cta: "Share slide 1 if this helped.",
    repurpose: "Longform LinkedIn article for AEO.",
    isVideo: false
  },
  {
    day: 4,
    week: 1,
    format: "Thread / Long Post (Operator Field Note #1)",
    headline: "Operator Field Note: Why follow-ups kill chair utilization — 7 real patterns",
    content: {
      sections: [
        { observation: "Pattern 1: The 48-hour drop-off", example: "Leads contacted after 48 hours convert 60% less", solution: "Implement same-day callback protocol" },
        { observation: "Pattern 2: The voicemail spiral", example: "Average clinic leaves 3.2 voicemails before giving up", solution: "Switch to multi-channel (text + email + call)" },
        { observation: "Pattern 3: The 'I'll call back' trap", example: "73% of 'call backs' never happen", solution: "Book the appointment during first contact" },
        { observation: "Pattern 4: Weekend lead death", example: "Friday-Sunday leads have 40% lower conversion", solution: "Monday morning priority queue" },
        { observation: "Pattern 5: The pricing question stall", example: "Leads asking price first often ghost", solution: "Qualify pain before discussing price" },
        { observation: "Pattern 6: The referral neglect", example: "Referrals convert 3x but get same follow-up as cold", solution: "VIP track for referral leads" },
        { observation: "Pattern 7: The no-show loop", example: "One no-show = 67% chance of churning", solution: "Confirmation sequence 24h + 2h before" }
      ]
    },
    cta: "I'll send the 1-page playbook — comment 'playbook'.",
    repurpose: "Gated Execution Gap Index snippet.",
    isVideo: false
  },
  {
    day: 5,
    week: 1,
    format: "Short Text (social proof)",
    headline: "A founder asked: 'Can we fix this in 60 days?' My answer: yes, if…",
    content: {
      conditions: [
        "You have at least 50 leads per month to work with (we need data to optimize)",
        "Someone on your team can own the implementation (we guide, you execute)",
        "You're willing to measure what matters, not just what's easy"
      ]
    },
    cta: "DM if you meet all three.",
    repurpose: "LinkedIn comment template for outreach scripts.",
    isVideo: false
  },
  {
    day: 6,
    week: 1,
    format: "Mini Case Study (anonymized)",
    headline: "How one clinic increased bookings +18% in 45 days (summary)",
    content: {
      before: "A 4-location dental practice was losing 35% of leads between inquiry and booking. No visibility into where leads were dropping off.",
      action: "Implemented operator-level tracking + automated follow-up sequences. Key change: text message within 5 minutes of inquiry.",
      outcome: "+18% bookings, $47K additional monthly revenue, follow-up time dropped from 4 hours to 12 minutes average."
    },
    cta: "Link to signup for pilot (gated).",
    repurpose: "60s video narrative.",
    isVideo: false
  },
  {
    day: 7,
    week: 1,
    format: "Engagement Play",
    headline: "What's the one SOP you refuse to automate?",
    content: {
      question: "Every operator has that one process they insist on keeping manual. What's yours?",
      context: "I'll start: We still manually review every customer escalation before responding. The nuance matters.",
      goal: "Pull comments and create debate (first-10min engagement group ready)"
    },
    cta: "Drop yours below — bonus points if you can defend it.",
    repurpose: "Compile responses into future content.",
    isVideo: false
  },

  // === WEEK 2: Education + Playbooks ===
  {
    day: 8,
    week: 2,
    format: "Text + Statistic",
    headline: "What we learned: 65% of missed revenue is from 3 small leaks",
    content: {
      leaks: [
        { leak: "Slow first response", stat: "23% of leads lost", fix: "Under 5-minute response target" },
        { leak: "No follow-up after voicemail", stat: "31% of leads lost", fix: "Multi-channel follow-up sequence" },
        { leak: "No-show without rebooking attempt", stat: "11% of leads lost", fix: "Same-day reschedule protocol" }
      ]
    },
    cta: "Reply '3 leaks' for a checklist.",
    repurpose: "Infographic for Instagram.",
    isVideo: false
  },
  {
    day: 9,
    week: 2,
    format: "60s Founder POV Video",
    headline: "I used to think automation means cost-cutting. I was wrong.",
    content: {
      hook: "I used to think automation means cost-cutting. I was wrong.",
      insight: "The best operators don't automate to reduce headcount. They automate to free up their best people for high-value conversations. One practice automated scheduling and their top closer now spends 100% of time on complex cases—revenue per patient up 22%.",
      duration: "60 seconds"
    },
    cta: "Comment 'proof' to get a 2-slide excerpt.",
    repurpose: "Quote graphic + thread.",
    isVideo: true,
    videoNote: "⚠️ VIDEO: This content requires hand-generated video. Record founder POV with direct camera address."
  },
  {
    day: 10,
    week: 2,
    format: "Thread (5 tweets/LinkedIn bullets)",
    headline: "10 micro-changes that increase appointment conversion — tested",
    content: {
      changes: [
        "1. Respond within 5 minutes (not 5 hours)",
        "2. Text before calling (67% higher answer rate)",
        "3. Mention the specific service they inquired about",
        "4. Offer 2 specific time slots, not 'when works for you'",
        "5. Confirm 24h AND 2h before appointment",
        "6. Send directions + parking info proactively",
        "7. Include a real human name, not just 'the team'",
        "8. Follow up no-shows within 1 hour",
        "9. Ask for referrals at peak satisfaction (right after appointment)",
        "10. Track which operator books each appointment"
      ]
    },
    cta: "Save this thread.",
    repurpose: "Checklist PDF lead magnet.",
    isVideo: false
  },
  {
    day: 11,
    week: 2,
    format: "Operator Field Note #2 (long)",
    headline: "The Execution Gap Index — sample insight: how PE-backed rollups leave money on the table",
    content: {
      intro: "We analyzed 23 PE-backed healthcare rollups. The pattern is consistent: acquisition = growth, but integration = chaos.",
      insights: [
        { finding: "Average time to standardize ops post-acquisition", data: "18 months", impact: "Lost revenue during integration: $2.3M average" },
        { finding: "Lead routing inconsistency", data: "67% of rollups have no unified system", impact: "Best locations subsidize worst performers" },
        { finding: "Operator performance visibility", data: "Only 12% track at individual level", impact: "Top performers leave, bottom performers hide" }
      ],
      conclusion: "The execution gap isn't about strategy. It's about the 47 small things that happen between 'we bought a company' and 'it's actually integrated.'"
    },
    cta: "Want the full index? Comment 'Index'.",
    repurpose: "Gated report + email sequence.",
    isVideo: false
  },
  {
    day: 12,
    week: 2,
    format: "Carousel: Playbook snippet",
    headline: "60-day pilot checklist — 7 steps",
    content: {
      slides: [
        { step: 1, title: "Baseline Metrics", description: "Document current conversion rates, response times, no-show rates before changing anything" },
        { step: 2, title: "Lead Source Audit", description: "Map every lead source and its conversion path. Find the leaks." },
        { step: 3, title: "Response Protocol", description: "Implement 5-minute response target with automated backup" },
        { step: 4, title: "Multi-Channel Sequences", description: "Build text + email + call follow-up flows" },
        { step: 5, title: "Operator Tracking", description: "Assign and measure at individual level, not just location" },
        { step: 6, title: "Weekly Reviews", description: "30-minute weekly check: what's working, what's not, what to adjust" },
        { step: 7, title: "ROI Calculation", description: "Compare Day 60 metrics to baseline. Calculate actual revenue impact." }
      ]
    },
    cta: "Share with a founder who needs this.",
    repurpose: "Email course content.",
    isVideo: false
  },
  {
    day: 13,
    week: 2,
    format: "Micro-poll",
    headline: "Quick poll for operators:",
    content: {
      question: "Which matters most to you right now?",
      options: [
        "Faster follow-ups",
        "Fewer no-shows",
        "Better pipeline visibility"
      ]
    },
    cta: "Vote and DM me why — I'll share the results.",
    repurpose: "Results become Day 26 content.",
    isVideo: false
  },
  {
    day: 14,
    week: 2,
    format: "Community Post",
    headline: "This operator did something unexpected — and it worked",
    content: {
      story: "Saw a post from [tag peer] about their no-show reduction strategy. Instead of more reminders, they started calling patients the day BEFORE to 'make sure they're still excited about their appointment.' Reframe: from nagging to caring.",
      amplify: "Sometimes the best ideas come from other operators, not consultants."
    },
    cta: "Want an intro to operators solving similar problems?",
    repurpose: "Build community engagement flywheel.",
    isVideo: false
  },

  // === WEEK 3: Credibility Amplification + Fellowship Launch ===
  {
    day: 15,
    week: 3,
    format: "Announcement Post (Operator Fellowship)",
    headline: "Announcing: AIGIS Operator Fellowship — learn how to run high-impact workflows",
    content: {
      what: "A 6-week intensive for operators who want to master AI-powered execution",
      who: "Healthcare operators, PE-backed practice managers, multi-location owners",
      reward: "Graduates get priority access to our pilot program + ongoing community"
    },
    cta: "Link to landing page — applications open.",
    repurpose: "X thread + email announcement.",
    isVideo: false
  },
  {
    day: 16,
    week: 3,
    format: "Testimonial Microvideo",
    headline: "What operators are saying about the Fellowship",
    content: {
      hook: "15s clip of a student or early user who saw a result",
      format: "Direct testimonial: 'Before AIGIS, I was spending 3 hours a day on follow-ups. Now it's 20 minutes.'",
      duration: "15-30 seconds"
    },
    cta: "Apply — 10 seats remaining.",
    repurpose: "Quote card + ad creative.",
    isVideo: true,
    videoNote: "⚠️ VIDEO: This content requires hand-generated video. Record testimonial from alumni/early user."
  },
  {
    day: 17,
    week: 3,
    format: "Thread: Qualification",
    headline: "How to qualify a pilot in 5 questions",
    content: {
      questions: [
        { q: "What's your current lead-to-appointment conversion rate?", why: "If they don't know, that's actually a good sign — they need help measuring" },
        { q: "How many leads do you get per month?", why: "Need at least 50 to have meaningful data" },
        { q: "Who handles follow-ups today?", why: "Need to identify the operator who'll own implementation" },
        { q: "What have you tried before?", why: "Previous failures = more motivated buyer" },
        { q: "What would 20% more bookings mean for your business?", why: "Anchor them to the outcome, not the process" }
      ]
    },
    cta: "Use this on your SDR call.",
    repurpose: "Sales enablement doc.",
    isVideo: false
  },
  {
    day: 18,
    week: 3,
    format: "Field Note #3: Fellowship Insights",
    headline: "The best leads come from curiosity, not cold lists — here's proof",
    content: {
      data: "Analyzed 200 pilot inquiries. The breakdown:",
      findings: [
        { source: "Content engagement (commented/DM'd)", conversion: "34% to pilot" },
        { source: "Referral from existing client", conversion: "28% to pilot" },
        { source: "Cold outreach (LinkedIn)", conversion: "3% to pilot" },
        { source: "Inbound from search", conversion: "18% to pilot" }
      ],
      insight: "The compound effect of consistent content > any cold outreach campaign."
    },
    cta: "Comment 'Fellow' to apply to the Fellowship.",
    repurpose: "Case for content-led growth.",
    isVideo: false
  },
  {
    day: 19,
    week: 3,
    format: "Heavy Value Carousel",
    headline: "Alternatives to hiring: ROI comparison (tool vs FDE vs hybrid)",
    content: {
      slides: [
        { option: "Hire a follow-up coordinator", cost: "$45-55K/year", rampTime: "3 months", scalability: "Limited to 1 person's capacity", roi: "Break-even at 8 months" },
        { option: "Software-only solution", cost: "$200-500/month", rampTime: "2 weeks", scalability: "Unlimited but impersonal", roi: "Positive at month 2" },
        { option: "Hybrid: AI + human escalation", cost: "$800-1500/month", rampTime: "4 weeks", scalability: "AI handles volume, humans handle complexity", roi: "Positive at month 1" },
        { option: "Our recommendation", cost: "Start hybrid, prove ROI, then decide on headcount", note: "Let data drive hiring decisions, not assumptions" }
      ]
    },
    cta: "Want the spreadsheet? Comment 'ROI'.",
    repurpose: "AEO page content.",
    isVideo: false
  },
  {
    day: 20,
    week: 3,
    format: "Founder Micro-essay",
    headline: "Why we only charge if you see ROI",
    content: {
      usVersion: "We've done enough pilots to know: if you don't see ROI in 60 days, either we failed or you weren't ready. Either way, you shouldn't pay.",
      ukVersion: "We've found that performance-based pricing aligns incentives. If the results aren't there, neither is the invoice.",
      reasoning: "This isn't generosity — it's confidence. We've measured our conversion rates. We know what works."
    },
    cta: "If you'd like to qualify, DM 'pilot'.",
    repurpose: "FAQ page content.",
    isVideo: false
  },
  {
    day: 21,
    week: 3,
    format: "Engagement Stunt",
    headline: "We're opening 3 pilot spots this week",
    content: {
      challenge: "Tell us your #1 operational pain in the comments. We'll pick 3 companies and offer a free 60-day pilot.",
      criteria: [
        "Must be a healthcare/dental/wellness practice",
        "Minimum 50 leads/month",
        "Ready to start within 2 weeks"
      ],
      selection: "We'll announce selections Friday."
    },
    cta: "Drop your pain point below — be specific.",
    repurpose: "Lead magnet + case study pipeline.",
    isVideo: false
  },

  // === WEEK 4: Scale and Signal Optimization ===
  {
    day: 22,
    week: 4,
    format: "Paid/Organic Hybrid",
    headline: "[BOOST] Operator Field Note performance",
    content: {
      action: "Boost a high-performing Operator Field Note post to targeted US dental operators and PE lists",
      targeting: "Healthcare operators, PE portfolio company leaders, multi-location practice owners",
      budget: "Start with $50-100/day, scale what works"
    },
    cta: "Same CTA as original post.",
    repurpose: "Paid amplification strategy.",
    isVideo: false,
    note: "📢 PAID PROMOTION: Boost your best-performing Field Note post from earlier in the month."
  },
  {
    day: 23,
    week: 4,
    format: "Longform LinkedIn Article (AEO focused)",
    headline: "How AI is recommended in 2025: owning the decision question (AEO playbook)",
    content: {
      sections: [
        { title: "The shift from SEO to AEO", content: "AI assistants don't show 10 blue links. They answer questions directly. The new game: be the answer, not a result." },
        { title: "What we're seeing", content: "Healthcare operators increasingly ask AI: 'What's the best way to improve patient follow-up?' If your content answers that question definitively, AI cites you." },
        { title: "The playbook", content: "1) Identify the 10 questions your ICP asks AI. 2) Create definitive answers. 3) Structure for AI readability. 4) Update quarterly." },
        { title: "Why this matters now", content: "Early movers in AEO are building moats. By 2026, the positions will be set." }
      ]
    },
    cta: "More AEO content on our site — link in comments.",
    repurpose: "Website page + SEO.",
    isVideo: false
  },
  {
    day: 24,
    week: 4,
    format: "Founder POV 1-min Video",
    headline: "If you're a PE operator, ask yourself this question",
    content: {
      hook: "If you're a PE operator, ask yourself: are you investing in growth or investing in execution?",
      script: "Most PE playbooks are 90% acquisition, 10% integration. But the money is made in the 10%. The practices that outperform don't just grow bigger—they grow better at the basics.",
      duration: "60 seconds"
    },
    cta: "Comment 'PE' for our operator integration checklist.",
    repurpose: "Thought leadership + targeting.",
    isVideo: true,
    videoNote: "⚠️ VIDEO: This content requires hand-generated video. Record founder POV with crisp 20s pitch."
  },
  {
    day: 25,
    week: 4,
    format: "Carousel: Fellowship Success Stories",
    headline: "What Fellowship graduates are achieving",
    content: {
      slides: [
        { name: "Graduate A", result: "Reduced follow-up time from 4 hours to 15 minutes", context: "Multi-location dental practice" },
        { name: "Graduate B", result: "Increased booking rate 23% in first month", context: "PE-backed wellness clinic" },
        { name: "Graduate C", result: "Now training their team on operator-level tracking", context: "Growing from 2 to 5 locations" },
        { callToAction: "Applications closing soon" }
      ]
    },
    cta: "Apply now — final cohort of 2025.",
    repurpose: "Social proof + urgency.",
    isVideo: false
  },
  {
    day: 26,
    week: 4,
    format: "Micro-survey Results",
    headline: "You voted — here's what operators care about most",
    content: {
      results: "From Day 13 poll:",
      data: [
        { option: "Faster follow-ups", percentage: "47%" },
        { option: "Fewer no-shows", percentage: "31%" },
        { option: "Better pipeline visibility", percentage: "22%" }
      ],
      analysis: "The follow-up obsession makes sense: it's the first domino. Fix response time, and no-shows drop. Fix no-shows, and pipeline becomes clearer."
    },
    cta: "DM 'follow-up' for our 5-minute response protocol.",
    repurpose: "Research fodder + social proof.",
    isVideo: false
  },
  {
    day: 27,
    week: 4,
    format: "Thread: Script Share",
    headline: "The follow-up script we use that moves 1 in 3 leads to call",
    content: {
      script: {
        text1: "Hi [Name]! This is [Your Name] from [Practice]. I saw you were interested in [Service]. Quick question: are you looking to get this done in the next 2 weeks, or just exploring options?",
        response1: "If '2 weeks': Great! I have two openings this week — Tuesday at 2pm or Thursday at 10am. Which works better?",
        response2: "If 'exploring': No problem! What's your biggest question about [Service]? I can send you some info that might help.",
        text2: "[Send within 5 minutes of inquiry. Text, don't call first.]"
      },
      results: "This sequence converts 34% of leads to booked calls. The key: qualifying question upfront."
    },
    cta: "Save this. Use it tomorrow.",
    repurpose: "SDR training content.",
    isVideo: false
  },
  {
    day: 28,
    week: 4,
    format: "Field Note #4 (Index teaser)",
    headline: "Execution Gap Index — Q4 Preview",
    content: {
      preview: "We're releasing the full Execution Gap Index next month. Here's a preview of what we're seeing:",
      findings: [
        "Average healthcare practice leaves 31% of revenue on the table due to execution gaps",
        "The #1 gap: response time (still averaging 4+ hours industry-wide)",
        "Practices that measure operator-level performance outperform by 2.3x",
        "AI-assisted follow-up is now table stakes, not competitive advantage"
      ]
    },
    cta: "Index full report: email us 'Index Report' for early access.",
    repurpose: "AEO + lead magnet + email list builder.",
    isVideo: false
  },
  {
    day: 29,
    week: 4,
    format: "Roundup Post",
    headline: "30 days of content — here's what we learned",
    content: {
      learnings: [
        "1. Specific data beats general advice (our case studies outperformed everything)",
        "2. Engagement posts drive reach, value posts drive leads",
        "3. The 'playbook' CTA works better than any other",
        "4. Video content is table stakes, but text+image still converts",
        "5. Consistency compounds — day 25 performed better than day 5 with similar content"
      ]
    },
    cta: "DM me if you want to talk about your content strategy.",
    repurpose: "Internal learnings doc + future content planning.",
    isVideo: false
  },
  {
    day: 30,
    week: 4,
    format: "Ask for Intros",
    headline: "I'm looking for introductions to 2 specific types of operators",
    content: {
      request: "If you know either of these people, I'd love an intro:",
      icp1: "1. PE operating partner or portfolio company CEO in healthcare (dental, wellness, med spa)",
      icp2: "2. Multi-location practice owner (3+ locations) who's frustrated with their current lead follow-up",
      offer: "In exchange: I'll give you early access to our Execution Gap Index + a free 30-minute consultation for anyone you refer."
    },
    cta: "DM me or tag them below.",
    repurpose: "Referral flywheel + warm outreach.",
    isVideo: false
  }
];

// Helper function to get content by day
export const getContentByDay = (day) => contentCalendar.find(c => c.day === day);

// Helper function to get content by week
export const getContentByWeek = (week) => contentCalendar.filter(c => c.week === week);

// Week themes
export const weekThemes = {
  1: { name: "Foundation + Authority", description: "Establish Operator Field Notes series" },
  2: { name: "Education + Playbooks", description: "Build trust & AEO" },
  3: { name: "Credibility Amplification + Fellowship Launch", description: "Launch Fellowship program" },
  4: { name: "Scale and Signal Optimization", description: "Push top-of-funnel" }
};
