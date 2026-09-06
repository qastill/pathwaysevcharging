
/* ============ PAPER: ASEAN EV COMPARATIVE ============ */
(function(){
 const box=document.getElementById('aseanFacts'); if(!box) return;

 const FACTS=[
  ["5×","rentang harga DC fast charging antar-negara ASEAN"],
  ["6","pasar dibandingkan · 5 arketipe struktur"],
  ["4.655","unit SPKLU Indonesia 2025 (+44%)"],
  ["31.859","target unit 2030 — pipeline terbesar di ASEAN"],
  ["≈67%","pangsa Indonesia dalam produksi nikel dunia"],
  ["106.644","penjualan BEV Indonesia 2025 (2× lipat)"],
 ];
 box.innerHTML=FACTS.map(f=>`<div class="f"><div class="n">${f[0]}</div><div class="l">${f[1]}</div></div>`).join('');

 const tbl=(id,head,rows)=>{
   const el=document.getElementById(id); if(!el) return;
   el.innerHTML='<table><thead><tr>'+head.map(h=>`<th>${h}</th>`).join('')+
     '</tr></thead><tbody>'+rows.map(r=>'<tr>'+r.map(c=>`<td>${c}</td>`).join('')+'</tr>').join('')+'</tbody></table>';
 };

 tbl('aseanT1',['Country','Main operators','DC price (local)','≈ USD/kWh','Tariff structure'],[
  ['<b>Vietnam</b>','V-Green (captive)','3,858 VND/kWh + idle fee 1,000 VND/min after 30 min','~0.148','Flat, VinFast vehicles only'],
  ['<b>Indonesia</b>','PLN SPKLU + partners','Rp2,466–2,475/kWh + service fee ≤Rp25k (fast) / ≤Rp57k (ultra) per session','~0.15 + session fee','Regulated energy tariff; capped per-session service fee (Kepmen ESDM 182.K/2023)'],
  ['<b>Thailand</b>','PEA Volta, EA Anywhere, EV Station PluZ, Shell, Onion','5.30–9.50 THB/kWh','0.16–0.29','Market-based; TOU (peak up to +40%)'],
  ['<b>Malaysia</b>','Gentari, JomCharge, ChargEV/TNB Electron','RM0.85–1.80/kWh; AC RM1.00–1.15','0.20–0.43','Market-based; location tiers; subscriptions (Gentari Go RM350–699/yr); idle fee RM0.40/min'],
  ['<b>Philippines</b>','ACMobility et al. (DOE-accredited)','₱20–38/kWh','0.35–0.67','Market-based; DOE accreditation required'],
  ['<b>Singapore</b>','SP Mobility, Shell Recharge, CDG ENGIE (29 operators)','S$0.55–0.89/kWh; AC S$0.45–0.82','0.43–0.70','Market pricing under LTA licence; idle fee S$0.50/min (cap S$40)'],
 ]);

 tbl('aseanT2',['Country','Archetype','Who may sell EV charging','Key policy instruments'],[
  ['<b>Vietnam</b>','Captive vertical integration','V-Green (VinFast vehicles only); franchisees under fixed 750 VND/kWh share; PV Power pilot emerging','Registration-fee waiver to 2027; ecosystem-subsidized pricing'],
  ['<b>Thailand</b>','Open multi-CPO','Any ERC-licensed operator (≥1,000 kVA: distribution licence; smaller: notification)','EV3.0/EV3.5 purchase subsidies; BOI tax holidays; DOEB technical rules (Apr 2026); TIS equipment standards 2027–28'],
  ['<b>Indonesia</b>','Utility-anchored partnership','PLN and Partnership-SPKLU partners (no separate IUPTL needed); regulated tariffs','Kepmen ESDM 182.K/2023 tariff caps; luxury-tax (PPnBM) exemption; 30% night home-charging discount'],
  ['<b>Singapore</b>','Licensed tender','LTA-licensed operators only (29 as of Jul 2026); certified &amp; registered chargers','EV Common Charger Grant; 60,000-point 2030 target; HDB EV-ready towns'],
  ['<b>Malaysia</b>','GLC-led hybrid','Gentari/TNB Electron plus private CPOs (no government funding; import duties; substation surrender to TNB)','20% EV sales target 2030; import/excise waivers for EVs; MEVnet monitoring'],
  ['<b>Philippines</b>','Mandate-driven early market','DOE-accredited providers only; per-site registration','EVIDA (RA 11697): 5% fleet mandate; zero-tariff imports; fuel-station charger obligation'],
 ]);

 tbl('aseanT3',['Dimension','Strengths','Weaknesses / risks'],[
  ['<b>Demand</b>','BEV sales doubled in 2025 (106,644 units); ≈15% BEV share, surpassing the US; largest ASEAN auto market by volume','Chinese brands (BYD group 51%) dominate — value capture partly offshore; 2025 sales figures differ across sources (99,755–106,644)'],
  ['<b>Infrastructure</b>','Largest deployment pipeline (4,655 → 31,859-unit target); +44% growth 2025; HCS subscriptions +118%; Partnership scheme lowers entry barriers (no IUPTL needed)','Utilization low outside Java; ultra-fast NPV negative in 5-yr horizon (Makassar case); archipelagic logistics; 1:21 charger-to-EV ratio vs 1:17 target'],
  ['<b>Pricing &amp; returns</b>','Affordable, predictable regulated tariffs; consumer trust; 30% night home-charging discount drives HCS uptake','Per-session service-fee caps (Rp25k/57k) bound CPO revenue; no TOU at public chargers; margin thinner than Thailand/Malaysia'],
  ['<b>Upstream</b>','≈67% of world nickel mine output; CATL ≈US$6bn integrated project; Hyundai–LGES 10 GWh operating','LG-led US$7.7bn project cancelled (Apr 2025) → concentration risk on Chinese partners; ≈66% coal grid weakens EV carbon case'],
  ['<b>Investment access</b>','PMA feasible at scale; four PLN partnership models incl. investor-own–operate; 25/73/2 revenue split published','Rp10bn minimum foreign investment per project area deters small entrants; utility-anchored structure limits pricing innovation'],
 ]);

 const REFS=[
  '[1] Maybank Research, cited in TNGlobal, "Southeast Asia’s EV sales accelerate as energy crisis continues," 27 August 2026. https://technode.global/2026/08/27/southeast-asias-ev-sales-accelerate-as-energy-crisis-continues/',
  '[2] Ember, "ASEAN emerges as a new leader in global EV adoption," 16 December 2025. https://ember-energy.org/latest-updates/asean-emerges-as-a-new-leader-in-global-ev-adoption/',
  '[3] Focus2move, "ASEAN Vehicle Market 2026," July 2026. https://www.focus2move.com/asean-vehicle-market/',
  '[4] PT PLN (Persero), "Permudah Mobilitas Kendaraan Listrik, PLN Operasikan 4.655 SPKLU Sepanjang 2025," siaran pers, 8 February 2026. https://web.pln.co.id/media/siaran-pers/2026/02/pln-operasikan-4655-spklu-permudah-mobilitas-kendaraan-listrik',
  '[5] Kementerian ESDM, Keputusan Menteri ESDM No. 182.K/TL.04/MEM.S/2023 tentang Biaya Layanan Pengisian Listrik pada SPKLU, 2023.',
  '[6] PT PLN (Persero), "Kesiapan Pengembangan Infrastruktur SPKLU," presentation to Direktorat Jenderal Ketenagalistrikan ESDM, 18 February 2025. https://gatrik.esdm.go.id/assets/uploads/download_index/files/ddde0-bahan-pln.pdf',
  '[7] V-Green, "Charging Station for Electric Cars — pricing," operator page, accessed 2026. https://vgreen.net/en/tram-sac-o-to-dien',
  '[8] V-Green, "V-Green pioneers the implementation of the EV charging franchise model in Vietnam," 2024. https://vgreen.net/en/v-green-pioneers-the-implementation-of-the-ev-charging-franchise-model-in-vietnam',
  '[9] VnExpress International, "V-Green deploys first EV charging station franchise model in Vietnam," 2024. https://e.vnexpress.net/news/business/companies/v-green-deploys-first-ev-charging-station-franchise-model-in-vietnam-4789409.html',
  '[10] Green Energy Thailand, "How Much Does EV Charging Cost in Thailand? 7-Eleven, MEA, PEA and Home Rates Compared," 2026. https://www.greenenergythailand.com/posts/much-charging-cost-thailand/',
  '[11] LTA DataMall and operator rate cards compiled by EV Charge Buddy and revolt.sg price index, Singapore, mid-2026. https://revolt.sg/ev-charging/price-index',
  '[12] Ministry of Transport Singapore, "Electric Vehicles," policy page (60,000-point 2030 target; installed-base updates), accessed 2026. https://www.mot.gov.sg/what-we-do/green-transport/electric-vehicles/',
  '[13] Malaysia4U / EV Sifu network guides and Gentari published tariffs (rev. March 2025; idle fee 30 March 2026), accessed 2026. https://malaysia4u.com/ev-charging-guide',
  '[14] MEVnet dashboard, Malaysian Green Technology and Climate Change Corporation (MGTC) / PLANMalaysia, charger census as of 31 March 2026.',
  '[15] The Edge Malaysia, "Lessons learnt from Malaysia’s missed target to build 10,000 EV charging points," 2025. https://theedgemalaysia.com/node/803636',
  '[16] Emerhub, "How to start an EV charging station business in the Philippines," accessed 2026. https://emerhub.com/philippines/how-to-start-an-ev-charging-station-business-in-the-philippines/',
  '[17] RichestPH / Top Gear Philippines, compiled Philippine public charging price surveys, 2025–2026.',
  '[18] DetikFinance, "Kendaraan Listrik Digenjot, SPKLU Ditambah hingga 31.859 Unit" (BKPM statement), 2025. https://finance.detik.com/energi/d-7732691/',
  '[19] PT PLN (Persero), "Partnership SPKLU," program page (schemes, revenue sharing, site requirements), accessed 2026. https://layanan.pln.co.id/partnership-spklu',
  '[20] Thailand Board of Investment, press release on EV supply-chain investment pledges (US$4.1 billion across 198 projects; BEV capacity &gt;370,000 units/yr), 3 July 2026.',
  '[21] ASEAN Briefing (Dezan Shira), "BOI EV 3.5 Policy in Thailand and EV Battery Investment Opportunities," 2024–2025. https://www.aseanbriefing.com/news/how-boi-ev-3-5-shapes-the-future-of-ev-battery-investments-in-thailand/',
  '[22] Bangkok Post, coverage of Department of Energy Business (DOEB) technical regulations for EV charging effective April 2026 (Dir-Gen Sarawut Kaewtathip).',
  '[23] Gaikindo wholesale data cited in Just Auto, Indonesia BEV sales 2025 (106,644 units; BYD group share 51%), January 2026.',
  '[24] ICCT, "Electric vehicle market in Indonesia," December 2025. https://theicct.org/publication/electric-vehicle-market-in-indonesia-dec25/',
  '[25] USGS, Mineral Commodity Summaries 2026 — Nickel (Indonesia mine production ~2.6 Mt of 3.9 Mt world total).',
  '[26] Tempo / Yonhap, "LG-led consortium cancels US$7.7 billion Indonesia Grand Package battery project," 18 April 2025.',
  '[27] Mordor Intelligence, "ASEAN Electric Vehicle Market (2026–2031)," market estimate USD 5.99B (2026) to USD 23.58B (2031), CAGR 31.55%; DC fast-charging CAGR 32.85%. https://www.mordorintelligence.com/industry-reports/asean-electric-vehicle-market',
  '[28] MarkWide Research, "ASEAN Electric Vehicle Market Forecast 2026–2036," alternative estimate USD 18.7B (2026) to USD 135.36B (2035), CAGR 24.60%. https://markwideresearch.com/asean-electric-vehicle-market',
  '[29] Electrive, "V-Green to build 99 fast-charging stations in Vietnam" (20 March 2026) and "V-Green opens Hanoi’s largest fast-charging station" (7 July 2025). https://www.electrive.com/',
  '[30] Studi kelayakan finansial SPKLU (kasus ULP Mattoanging, Makassar): Fast Charging NPV Rp108 juta, IRR 45%; Ultra-Fast Charging NPV negatif dalam horizon lima tahun. Jurnal ilmiah Indonesia, 2024–2025.',
  '[31] KrASIA / Nikkei Asia, "EV boom drives ASEAN car sales in Q2, with Indonesia surging 34%," August 2026. https://kr-asia.com/ev-boom-drives-asean-car-sales-in-q2-with-indonesia-surging-34',
  '[32] Benchmark hardware and installation cost compilations for AC/DC/ultra-fast chargers (Klitv, QuikrEV, BENY, SolarTech, TrendX Insights), 2025–2026; IEA Global EV Outlook on ultra-fast hardware cost decline (≈20%, 2022–2024).',
 ];
 const linkify=s=>s.replace(/(https?:\/\/[^\s]+)/g,'<a href="$1" target="_blank" rel="noopener" style="color:var(--blue)">$1</a>');
 document.getElementById('aseanRefs').innerHTML=REFS.map(r=>`<div>${linkify(r)}</div>`).join('');
})();
