import { request, gql } from 'graphql-request';

async function fetchDailyVolume() {
  const endpoint = 'https://api.goldsky.com/api/public/project_clrhmyxsvvuao01tu4aqj653e/subgraphs/supswap-exchange-v3/1.0.0/gn';

  // get utc date in seconds
  const date: number = parseInt((new Date().getTime() / 1000).toString());
  const id: string = Math.floor(date / 86400).toString();

  const volumeQuery = gql`
    query($id: String!) {
      supDayData(id: $id) {
        volumeUSD
      }
    }
  `;

  try {
    const volumeData: any = await request(endpoint, volumeQuery, { id });
    console.log(`Daily Volume: ${volumeData.supDayData.volumeUSD}`);
  } catch (e) {
    console.error(e);
  }

  // get utc timestamp for start of day
  const now = new Date();
  const dayStart = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate(), 0, 0, 0, 0));
  const dayStartId = Math.floor(dayStart.getTime() / 1000);

  
  var allSwaps = new Set();
  try {
    var keepFetching = true;
    var pageIndex = 0;
    const perPage = 1000;
    while (keepFetching) {
      const swapsQuery = gql`
        query {
          swaps(skip: ${pageIndex * perPage}, first: ${perPage}, orderBy: timestamp, where: {timestamp_gt: ${dayStartId}}) {
            id
          }
        }
      `
      const swapsData: any = await request(endpoint, swapsQuery);
      const { swaps } = swapsData;
      for (let swap of swaps) {
        if (allSwaps.has(swap.id)) {
          keepFetching = false;
          break;
        } allSwaps.add(swap.id);
      }
      if (swaps.length != 1000) {
        keepFetching = false;
        break;
      }
      pageIndex += 1;
    
    }
    console.log(`Daily Swaps: ${allSwaps.size}`);     
  } catch (e) {
    console.error(e);
  }
};

fetchDailyVolume();