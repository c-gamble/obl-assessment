import BigNumber from "bignumber.js";
import { CHAINS, PROTOCOLS, AMM_TYPES } from "./sdk/config";
import { getLPValueByUserAndPoolFromPositions, getPositionAtBlock, getPositionDetailsFromPosition, getPositionsForAddressByPoolAtBlock } from "./sdk/subgraphDetails";
import fs from 'fs';

(BigInt.prototype as any).toJSON = function () {
  return this.toString();
};


function writeToFile(text: string, path: string) {
  fs.appendFileSync(path, text);
}

const mapToObj = (m: Map<any, any>) => {
  return Array.from(m).reduce((obj: any, [key, value]) => {
    obj[key] = value;
    return obj;
  }, {});
};

interface UserData {
  'id': string,
  'pools': Map<string, BigNumber>,
  'total': BigNumber,
}

interface BlockData { 
  users: UserData[];
  positions: Number;
}

async function getData (out: string) {

var saveData: { blocks: BlockData[] } = {
  'blocks': []
}
const snapshotBlocks = [
  0
];

for(let block of snapshotBlocks) {

  const positions = await getPositionsForAddressByPoolAtBlock(
    block, // block number 0 for latest block
    "",  //pass empty string to remove filter based on user address
    "",  //pass empty string to remove filter based on pool address
    CHAINS.MODE, // chain id
    PROTOCOLS.SUPSWAP, // protocol
    AMM_TYPES.UNISWAPV3 // amm type
  );
 console.log(`Block: ${block}`);
 // writeToFile(`Block: ${block}\n`, out);
 saveData.blocks.push({'users': [], 'positions': positions.length});

    // print response

    console.log("Positions: ", positions.length)
    // writeToFile(`Positions: ${positions.length}\n`, out);

    let positionsWithUSDValue = positions.map((position) => {
      return getPositionDetailsFromPosition(position);
    });

    let lpValueByUsers = getLPValueByUserAndPoolFromPositions(positionsWithUSDValue);

    let onlyUsersWithLPValue = new Map<string, BigNumber>();

    lpValueByUsers.forEach((value, key) => {
      let lpValue: Map<string, BigNumber> = value;
      let total = new BigNumber(0);
      lpValue.forEach((value, key) => {
        total = total.plus(value);
      }
      );
      onlyUsersWithLPValue.set(key, total);
    });


    //sort onlyUsersWithLPValue by value
    let sortedLpValueByUsers = new Map([...onlyUsersWithLPValue.entries()].sort((a, b) => {
      return b[1].comparedTo(a[1]);
    }));
    let protocolTotal = new BigNumber(0);
    sortedLpValueByUsers.forEach((value, key) => {
      protocolTotal = protocolTotal.plus(value);
    });

    sortedLpValueByUsers.forEach((value, key) => {
      console.log(`User: ${key}`);
      // writeToFile(`User: ${key}\n`, out);

      var userPools = new Map<string, BigNumber>();

      let lpValue: Map<string, BigNumber> = lpValueByUsers.get(key)||new Map();
      let total = new BigNumber(0);
      lpValue.forEach((value, key) => {
        console.log(`Pool: ${key} LP Value: ${value.toString()}`);
        // writeToFile(`Pool: ${key} LP Value: ${value.toString()}\n`, out);
        total = total.plus(value);

        userPools.set(key, value);
      }
      );
      saveData.blocks[saveData.blocks.length - 1].users.push({'id': key, 'pools': mapToObj(userPools), 'total': total});
      console.log("User's total LP", total.toString());
      console.log("---------------------------------------------------");
      // writeToFile(`User's total LP: ${total.toString()}\n`, out);
      // writeToFile(`---------------------------------------------------\n`, out);
    });

    const json = JSON.stringify(saveData);
    fs.writeFileSync(out, json);

    console.log("Protocol's total LP", protocolTotal.toString());
    // writeToFile(`Protocol's total LP: ${protocolTotal.toString()}\n`, out);
}
}

const outputPath = '/Users/coopergamble/code/openblock/assessment/task5/rawData.json';
getData(outputPath);