from pydantic import BaseModel
from langgraph.types import Command, interrupt
from langchain.tools import tool



@tool
def transfer(address: str, amount: int) -> str:
    """
    사용자가 입력한 송금 정보를 (중간에 사용자의 요청으로 정보가 변경될 수 있음) 송금하는 함수입니다.
    이 도구를 사용 한 후 어떤 계좌로 얼마가 송금되었는지 도구의 출력을 바탕으로 말하시오.
    """

    human_response = interrupt({'address': address, 'amount': amount})

    return f"최종 확인된 정보에 따라 {human_response['address']} 계좌로 {human_response['amount']}원을 송금했습니다."


@tool
def getAccountBalance() -> dict:
    """get account balance"""
    return {
        'TEST-ADDRESS' : 300000
    }

