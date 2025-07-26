import binascii
import hashlib
import os
from typing import Optional


def generate_salt(length: int = 16):
    """生成随机盐值（默认16字节）"""
    return os.urandom(length)


def sha256_with_salt(target: str, salt: Optional[bytes] = None):
    """对密码进行加盐哈希处理"""
    # 如果没有提供盐值，则生成新盐
    if salt is None:
        salt = generate_salt()

    # 将密码编码为字节，加盐后计算哈希
    encoded_bytes = target.encode("utf-8")
    salted_bytes = salt + encoded_bytes
    hash_obj = hashlib.sha256(salted_bytes)
    hash_digest = hash_obj.digest()

    # 返回十六进制格式的盐值和哈希值
    return binascii.hexlify(salt).decode("utf-8"), binascii.hexlify(hash_digest).decode("utf-8")


def verify_hashed(target: str, stored_salt_hex: str, stored_hash_hex: str):
    """验证输入的密码是否正确"""
    # 将存储的十六进制盐值和哈希值转换为字节
    stored_salt = binascii.unhexlify(stored_salt_hex)
    stored_hash = binascii.unhexlify(stored_hash_hex)

    # 使用相同方法计算输入密码的哈希
    _, new_hash = sha256_with_salt(target, salt=stored_salt)
    new_hash_bytes = binascii.unhexlify(new_hash)

    # 使用恒定时间比较防止时序攻击
    return hashlib.sha256(new_hash_bytes).digest() == hashlib.sha256(stored_hash).digest()
