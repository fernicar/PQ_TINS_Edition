import base64
import os

def decode_pqw_file(pqw_file, output_file=None):
    """Decode a .pqw file and optionally save to output json file."""
    try:
        # Read the base64 encoded data
        with open(pqw_file, 'r') as f:
            encoded_data = f.read()
        
        # Decode the base64 data
        try:
            decoded_data = base64.b64decode(encoded_data).decode('utf-8')
        except Exception as e:
            print(f"Error decoding base64 data: {e}")
            # Try with different padding
            for padding in ['', '=', '==', '===']:
                try:
                    padded_data = encoded_data + padding
                    decoded_data = base64.b64decode(padded_data).decode('utf-8')
                    print(f"Successfully decoded with padding: '{padding}'")
                    break
                except:
                    continue
            else:
                print("Failed to decode with all padding options")
                return None
        
        # Save to output file if specified
        if output_file:
            with open(output_file, 'w') as f:
                f.write(decoded_data)
            print(f"Decoded data saved to {output_file}")
        
        return decoded_data
    
    except Exception as e:
        print(f"Error processing file {pqw_file}: {e}")
        return None

def compare_files(file1, file2):
    """Compare the content of two files."""
    try:
        with open(file1, 'r') as f1, open(file2, 'r') as f2:
            content1 = f1.read()
            content2 = f2.read()
        
        if content1 == content2:
            print(f"Files {file1} and {file2} have identical content")
        else:
            print(f"Files {file1} and {file2} have different content")
            # Show first few differences
            for i, (c1, c2) in enumerate(zip(content1, content2)):
                if c1 != c2:
                    print(f"First difference at position {i}: '{c1}' vs '{c2}'")
                    print(f"Context: '{content1[max(0, i-10):i+10]}' vs '{content2[max(0, i-10):i+10]}'")
                    break
            
            # Check if one is a subset of the other
            if content1 in content2:
                print("First file's content is contained within the second file")
            elif content2 in content1:
                print("Second file's content is contained within the first file")
            
            # Check length difference
            print(f"Length difference: {len(content1)} vs {len(content2)} characters")
    
    except Exception as e:
        print(f"Error comparing files: {e}")

if __name__ == "__main__":
    # File paths
    pqw_file = "fernicar.pqw"
    json_file = "fernicar.json"
    decoded_file = "fernicar_decoded.json"
    
    # Decode the .pqw file
    decoded_data = decode_pqw_file(pqw_file, decoded_file)
    
    if decoded_data:
        # Compare with the .json file
        compare_files(decoded_file, json_file)
        
        # Print a sample of the decoded data
        print("\nSample of decoded data:")
        print(decoded_data[:500] + "..." if len(decoded_data) > 500 else decoded_data)