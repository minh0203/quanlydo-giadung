import bcrypt


class PasswordUtils:
    """Tiện ích xử lý mã hóa mật khẩu"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Mã hóa mật khẩu sử dụng bcrypt
        
        Args:
            password (str): Mật khẩu gốc
            
        Returns:
            str: Mật khẩu đã mã hóa
        """
        if not password:
            return ""
        
        # Mã hóa mật khẩu với bcrypt
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        Xác minh mật khẩu với mã hóa
        
        Args:
            password (str): Mật khẩu nhập vào
            hashed_password (str): Mật khẩu đã mã hóa từ database
            
        Returns:
            bool: True nếu mật khẩu đúng, False nếu sai
        """
        if not password or not hashed_password:
            return False
        
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception:
            return False
